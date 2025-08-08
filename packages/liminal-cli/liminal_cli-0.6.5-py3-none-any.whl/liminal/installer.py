"""
gets us set up on a server so the users shell history is synced


TODO:
- retry endpoints

future - 
share to shared spot on server
liminal CLI - generate report, get help

errror messages and handling is a little spaghetti



"""

import http
import json
import os
import re
import subprocess
import sys
import time
import traceback
import uuid

from pathlib import Path

import requests

from liminal import atuin, LIMINAL_PACKAGE_VERSION
from liminal.config import Config
from liminal.datetime_util import datetime_utcnow
from liminal.env import LAST_SUCCESS_INSTALL_FLAG_PATH, debug, get_os_distro_info
from liminal import EMAIL_CONTACT, LIMINAL_BIN, LIMINAL_DIR
from liminal.logging import INSTALL_LOG_PATH, LOGGER, enable_sending_prints_to_logger
from liminal.command_runner import debug_shell_startup, run_command
from liminal.session import InstallationSession
from liminal.shell import path_replace_home_with_var, determine_shell, Shell

LIMINAL_SHELL_EXTENSION = LIMINAL_DIR / 'shell-extension.sh'

STANDALONE_SHELLSYNC_APP_URL = f'https://{Config.HOST}'
USER_INSTALL_KEY_URL = f'{STANDALONE_SHELLSYNC_APP_URL}/docs/install'
USER_INPUTED_INSTALL_TOKEN = os.environ.get('LIMINAL_INSTALL_TOKEN')
MAIN_LIMINAL_URL = 'https://liminalbios.com/'
INSTALL_SESSION: InstallationSession | None = None

USER_SHELL: Shell = Shell() 

PROGRESS_TRACKER = {
	# Store progress throughout the script, so we can include in our logs
	# TODO: could replace with a filtered install log
}


def set_progress(checkpoint_name: str, value):
	global PROGRESS_TRACKER
	LOGGER.debug(f'progress_tracker: {checkpoint_name}={value}')
	PROGRESS_TRACKER[checkpoint_name] = value
	if Config.LIMINAL_INSTALLER_PAUSE_AT == checkpoint_name:
		LOGGER.debug('checkpoint paused')
		input(f'\n\nPausing at {checkpoint_name=}....Press any key to continue:')



class DependencyError(Exception):
	pass

class ExpiredToken(Exception):
	pass

class UserMessagableError(Exception):
	# for errors were we only need to show the user a message
	pass


class Server: # SyncAPI
	API_ADDRESS = Config.API_ADDRESS
	SYNC_ADDRESS = Config.ATUIN_SYNC_ADDRESS

	def verify_sync(self, expected_details):
		LOGGER.debug(f'{expected_details=}')
		payload = {
			'expected_history': expected_details,
			'liminal_user_uuid': INSTALL_SESSION.liminal_user_uuid
		}
		resp = requests.post(f'{self.API_ADDRESS}/install/verify-command', json=payload, timeout=10, headers=get_headers())
		try:
			self.assert_response_ok(resp)
		except AssertionError as e:
			e.add_note('Server was not able to process the test shell command')
			raise e


	def test_connection(self):
		try:
			resp = requests.get(f'{self.API_ADDRESS}/health', timeout=5)
			self.assert_response_ok(resp)
			LOGGER.info(f'{self.API_ADDRESS} is available')
		except Exception as e:
			raise AssertionError(f'Issue connecting to server {self.API_ADDRESS}') from e
		

	def authenticate_user_provided_key(self, install_token: str, install_uuid: str) -> InstallationSession:
		LOGGER.debug(f'going to verify install token {install_token}')
		headers = {'Authorization': f'Bearer {USER_INPUTED_INSTALL_TOKEN}'}
		payload_for_server = {
			'install_uuid': install_uuid,
		}
		resp = requests.post(f'{self.API_ADDRESS}/user/validate', json=payload_for_server, timeout=10, headers=headers)
		resp_body = resp.json()
		if resp.status_code == http.HTTPStatus.FORBIDDEN and resp_body['description'] == 'Token is expired':
			raise ExpiredToken()

		if resp.status_code == http.HTTPStatus.UNAUTHORIZED and resp_body['description'].endswith('User is not registered on Liminal.'):
			raise UserMessagableError("\nStopping install...\nYou are not a registered user of Liminal :'( Please sign up in order to finish installation.")
		
		# if resp.status_code == http.HTTPStatus.FORBIDDEN and resp_body['description'].startswith('User has already completed an install'):
		# 	old_install_id = resp_body['install_id']
		# 	raise UserMessagableError(f'\nStopping install...\nPreviously completed installation {old_install_id}.\nContact support.')
		


		self.assert_response_ok(resp, error_suffix=f' Invalid token {install_token}')
		set_progress('user_is_verified', True)
		resp_body = resp.json()
		user_id = resp_body['liminal_user_uuid']
		LOGGER.debug(f'Validated the user id as liminal user {user_id} {resp_body=}')
		return InstallationSession(api_address=self.API_ADDRESS, **resp_body)


	@classmethod
	def assert_response_ok(cls, response: requests.Response, error_suffix: str = ''):
		assert response.ok, f'Bad Response: {response.url}: {response.status_code} {response.reason}: {response.text}' + error_suffix


def test_environment():
	"""
	assert atuin isn't already installed. exit if it is.
	
	"""
	shell = USER_SHELL
	assert shell.is_supported()
	set_progress('shell_is_supported', True)

	shell._bash_config_creation()
	shell.try_parse_login_command()
	set_progress('shell_is_parseable', True)

	try:
		assert shell.is_config_writable()
	except AssertionError:
		raise UserMessagableError(f'You do not have write access to {shell.config_file}, and we cannot continue')
	set_progress('shell_is_configurable', True)

	if not atuin.is_the_users_existing_atuin_env_supported(progress_setter=set_progress):
		set_progress('atuin_env_is_supported', False)
		raise RuntimeError("""Atuin is already installed with syncing. We dont yet support existing atuin syncs""")
	set_progress('atuin_env_is_supported', True)

	required_tools = ['curl', 'sed']
	# TODO: better config startup checks. assert file exists too
	if Config.LIMINAL_INSTALLER_ATUIN_HISTORY_SEED_FILE:
		required_tools.append('sqlite3')
	missing_tools = []
	for tool in required_tools:
		try:
			subprocess.run(f'command -v {tool}', shell=True, executable=shell.exec_path.as_posix(), check=True, capture_output=True)
			# NOTE: shell=True needed because env=os.environ.copy() no work
		except (subprocess.CalledProcessError, FileNotFoundError):
			missing_tools.append(tool)
	if missing_tools:
		raise DependencyError(f'Missing the following CLI tools: {missing_tools}')
	set_progress('prereq_tools_are_installed', True)

	Server().test_connection()
	set_progress('server_connection_good', True)



def preflight_tests():
	LOGGER.info('Running preflight checks')
	test_environment()




def test_correctly_setup():
	"""
	- run a command and make sure it syncs, and that the server can decrypt it
	"""
	LOGGER.info('Checking installation works as expected')

	assert atuin.Paths.HISTORY_DB.exists()
	local_test_command_entry = atuin.test_atuin_recording_locally(USER_SHELL)

	Server().verify_sync(local_test_command_entry)
	set_progress('correctly_setup', True)



class ShellConfig:

	def __init__(self, shell: Shell = None):
		self.shell: Shell = shell or Shell()

	def generate_extension_file(self):
		shell = self.shell
		LIMINAL_BIN.mkdir(exist_ok=True)
		bash_preexec_path = LIMINAL_DIR / 'bash-preexec.sh'
		# TODO: maybe just include with our package? would be more reliable
		if shell.is_bash():
			commit = 'e8e9024d4d101a69016169e46f5d75df3fdb7e32'
			url = f'https://raw.githubusercontent.com/rcaloras/bash-preexec/{commit}/bash-preexec.sh'
			response = requests.get(url, timeout=10)
			bash_preexec_path.write_bytes(response.content)

		template = (Path(__file__).parent / 'shell-extension_template.txt').read_text()
		content = template.format(shell_name=shell.exec_path.name, bash_preexec_path=path_replace_home_with_var(bash_preexec_path))
		LIMINAL_SHELL_EXTENSION.write_text(content)


	def add(self):
		# TODO: backup their file
		current_config_content = self.shell.config_file.read_text()
		extension_source_path = path_replace_home_with_var(LIMINAL_SHELL_EXTENSION)
		
		template = (Path(__file__).parent / 'shell-rc_load-extension_template.txt').read_text()
		loader_block_content = template.format(
			info_url=MAIN_LIMINAL_URL, LIMINAL_PACKAGE_VERSION=LIMINAL_PACKAGE_VERSION, 
			install_date=datetime_utcnow(), extension_source_path=extension_source_path
		)
		existing_breadcrumb_pattern = '^### Liminal tools ---.*^### --- Liminal tools'

		if (match := re.search(existing_breadcrumb_pattern, current_config_content, flags=re.MULTILINE | re.DOTALL)):
			LOGGER.debug('existing block found', extra={'content': match.group()})
			updated_file_content = re.sub(existing_breadcrumb_pattern, loader_block_content, current_config_content, flags=re.MULTILINE | re.DOTALL)
		else:
			updated_file_content = current_config_content + '\n\n' + loader_block_content + '\n'
		self.shell.config_file.write_text(updated_file_content)






def get_headers():
	return {'Authorization': f'Bearer {INSTALL_SESSION.cli_api_access_token}'}

def copy_key_to_server(liminal_user_uuid: str):
	LOGGER.info('Copying atuin key to enable report generation')
	key_file = atuin.Paths.KEY_FILE
	host_id = atuin.get_host_id()
	files = {
		'file_content': ('key', key_file.open(mode='rb'))
	}
	data = {
		'metadata': json.dumps({
			'liminal_user_uuid': liminal_user_uuid,
			'atuin_host_id': host_id,
			'install_id': INSTALL_SESSION.install_id,
		})
	}
	response = requests.post(f'{Server.API_ADDRESS}/install/key', data=data, files=files, headers=get_headers(), timeout=10)
	Server.assert_response_ok(response)
	set_progress('key_copied_to_server', True)


def handle_user_install_token():
	global USER_INPUTED_INSTALL_TOKEN
	global INSTALL_SESSION
	install_uuid = str(uuid.uuid4()) # migh tneed replace dashes for atuin?
	LOGGER.debug(f'Starting ---------- {install_uuid}')

	print('\n###\nWelcome! The shell sync installation is starting')
	print(f'If you haven\'t already, get your install token from {USER_INSTALL_KEY_URL}\n')

	if USER_INPUTED_INSTALL_TOKEN:
		LOGGER.info(f'Using install token from env: LIMINAL_INSTALL_TOKEN={USER_INPUTED_INSTALL_TOKEN}')
	try:
		while not INSTALL_SESSION:
			if not USER_INPUTED_INSTALL_TOKEN:
				USER_INPUTED_INSTALL_TOKEN = input('\nPlease paste your Liminal install token: ').strip()
			try:
				INSTALL_SESSION = Server().authenticate_user_provided_key(USER_INPUTED_INSTALL_TOKEN, install_uuid)
			except ExpiredToken:
				USER_INPUTED_INSTALL_TOKEN = None
				INSTALL_SESSION = None
				LOGGER.error(f'Your install token has expired. Please generate a new one by visiting {USER_INSTALL_KEY_URL}')
			except UserMessagableError as e:
				LOGGER.debug('expected error', stack_info=True)
				print(*e.args) # the string (or list of strings) passed to the exception
				sys.exit(2)
	except KeyboardInterrupt:
		LOGGER.debug('user quit')
		sys.exit(2)

	INSTALL_SESSION.save()
	print(f'\nVerified as {INSTALL_SESSION.username}\n')


def _main():
	"""
	"""
	global USER_SHELL
	enable_sending_prints_to_logger(LOGGER)

	# do this first so we have install_id for all submitted errors
	handle_user_install_token()

	USER_SHELL = determine_shell(on_conflict_ask_user=True)
	preflight_tests()

	atuin.check_login_user_is_expected(INSTALL_SESSION.liminal_user_uuid.replace('-', ''))

	shellconfig = ShellConfig(shell=USER_SHELL)
	shellconfig.generate_extension_file()
	shellconfig.add()
	# TODO: if atuin is installed already by user, we might need to update their shell config so it doesnt load/init atuin twice

	if atuin.is_atuin_installed():
		atuin.upgrade()
	else:
		atuin.install_atuin(shellconfig.shell.exec_path)
		set_progress('did_install_atuin_in_this_session', True)
		# now import history so the sqlite db will exist, and then we can test it
		did_import_history = atuin.import_existing_history(USER_SHELL)
		set_progress('did_import_history', did_import_history)

	atuin.test_atuin_recording_locally(USER_SHELL)
	set_progress('local_atuin_history_working', True)

	atuin.configure_atuin(USER_SHELL, Server.SYNC_ADDRESS, freq='1hr') # preven sync on following register command?

	ATUIN_REGISTRATION_PASSWORD = str(uuid.uuid4()) # can be random and forgotten since this is for logging in on other machine. if users request in future they want to sync multiple machines, a future update can reset their password
	env_copy = os.environ.copy()
	env_copy['ATUIN_REGISTRATION_PASSWORD'] = ATUIN_REGISTRATION_PASSWORD
	atuin_username = INSTALL_SESSION.liminal_user_uuid.replace('-', '')
	register_task = run_command([atuin.Paths.EXECUTABLE, 'register', '-u', atuin_username, '-e', f'{INSTALL_SESSION.liminal_user_uuid}@forward.shellsync.liminalbios.com', '-p', '$ATUIN_REGISTRATION_PASSWORD'], env=env_copy, check=False)
	if register_task.returncode != 0:

		# for now, we will do a hard reset on the user - basically delete their atuin account and redo
		# this is ok to do for a single machine, but not multiple
		# TODO: only do delete if user has not done a succesful install. it is NOT OK to do this hard reset multiple times if there wasn't an install issue. 
		# 	like imagine you run the installer again a few days later after reports are generated, 
		# 	then all the relations will be messed up
		# 
		if 'Error: username already in use' in register_task.stderr:
			LOGGER.info('Re-registering your account')
			run_command([atuin.Paths.EXECUTABLE, 'account', 'delete'])
			set_progress('atuin_account_deleted', True)
			run_command([atuin.Paths.EXECUTABLE, 'register', '-u', atuin_username, '-e', f'{INSTALL_SESSION.liminal_user_uuid}@forward.shellsync.liminalbios.com', '-p', '$ATUIN_REGISTRATION_PASSWORD'], env=env_copy)
			# FUTURE:
			# env_copy['TODO_GET_ATUIN_ACCOUNT_PASSWORD'] = ''
			# env_copy['ATUIN_KEY'] = atuin.Paths.KEY_FILE.read_text()
			# run_command([atuin.Paths.EXECUTABLE, 'login', '-u', atuin_username, '--password', '$TODO_GET_ATUIN_ACCOUNT_PASSWORD', '--key', '$ATUIN_KEY'], env=env_copy)
			# set_progress('atuin_account_login', True)
		else:
			raise Exception(f'Issue with registration: {register_task.returncode}: {register_task.stdout=}\n{register_task.stderr=}')


	set_progress('atuin_account_registered', True)
	copy_key_to_server(INSTALL_SESSION.liminal_user_uuid)
	# TODO: revisit if we still need to set this twice after host_id fix
	atuin.configure_atuin(USER_SHELL, Server.SYNC_ADDRESS, freq='0')
	set_progress('atuin_configured_freq0', True)

	test_correctly_setup()

	LAST_SUCCESS_INSTALL_FLAG_PATH.write_text(json.dumps({'date': datetime_utcnow().isoformat(), 'version': LIMINAL_PACKAGE_VERSION}))
	LOGGER.debug('Finished local work sucessfully')

	try:
		atuin_host_id = atuin.get_host_id()
	except Exception:
		atuin_host_id = None
	
	confirmation_payload = {
		'liminal_user_uuid': INSTALL_SESSION.liminal_user_uuid,
		'python_version': sys.version,
		'shell': USER_SHELL.dict(),
		'os_distribution': get_os_distro_info(),
		'liminal_version': LIMINAL_PACKAGE_VERSION,
		'local_history_summary': atuin.local_history_summary().__dict__,
		'atuin_host_id': atuin_host_id,
		'install_id': INSTALL_SESSION.install_id,
	}
	LOGGER.debug('sending confirmation')
	confirm_response = requests.post(
		f'{Server.API_ADDRESS}/install/confirmation', timeout=10, headers=get_headers(), 
		json=confirmation_payload,
	)

	# unfortunately we need the confirmation to be sucessful so we can kick off work on the server
	try:
		Server.assert_response_ok(confirm_response)
	except AssertionError as e:
		raise UserMessagableError(f'Error: Was not able to do final confirmation with {STANDALONE_SHELLSYNC_APP_URL}') from e
		
	LOGGER.debug(f'All done {INSTALL_SESSION.install_id=}')



def cleanup():
	"""Cleanup any mess made by _main(), and make subsequent install attempts possible
	"""
	if Config.LIMINAL_INSTALLER_SKIP_CLEANUP == 'yes':
		LOGGER.debug('skipping cleanup')
		return
	if PROGRESS_TRACKER.get('did_install_atuin_in_this_session'):
		try:
			atuin.uninstall_atuin()
		except Exception:
			LOGGER.debug('issue uninstalling atuin', exc_info=True)
	
	# TODO: if registered_user_to_atuin, unregister them or handle in some way so they can run installer again


def print_user_stats():
	env_copy = os.environ.copy() | atuin.neccessary_atuin_env_vars()
	stats = run_command([atuin.Paths.EXECUTABLE, 'stats'], env=env_copy, check=False)
	# ^check=false so we dont log anything to user if error
	if stats.returncode == 0:
		print('\nYour top 10 most ran commands:')
		print(stats.stdout)


def main():
	try:
		_main()
	except Exception as e:
		report_install_issue(e)
		cleanup()
		exit(1)

	print('\n\n#################################################')
	# print('Liminal\'s `liminal_cl` tool has been installed!!\n')
	print('#################################################\n')
	print(f'Your command history will now be continuously synced to {STANDALONE_SHELLSYNC_APP_URL} (powered by `atuin`)')
	print('If you run into any issues or want to learn more, run `liminal_cl --help`')
	print_user_stats()
	print('\nFor everything to work properly, please exit this terminal and start a new one')

	# https://docs.atuin.sh/guide/basic-usage/

	sync_log = LIMINAL_DIR / 'nohup_sync.out'
	with sync_log.open(mode='w') as output_file:
		sync_command = ['nohup', sys.executable, '-m', 'liminal.cli', 'shell', 'sync', '--install-id', INSTALL_SESSION.install_id]
		# log this for easy copy/paste for devx
		LOGGER.debug('running sync in background:' + ' '.join(sync_command))
		try:
			child = subprocess.Popen(sync_command, stdout=output_file, stderr=output_file,)
			# give it just a little bit to start, and poll to potentially get some better output if exception?
			time.sleep(0.1)
			child.poll()
		except subprocess.CalledProcessError as e:
			LOGGER.warning('Issue initiating final sync')
			LOGGER.debug(f'{sync_log.read_text()=}')
	# TODO:
	# if atuin.local_history_count() > 2000:
	# 	print('command history might take 1-3 minutes to sync')
	# 	# `atuin sync` # run it so it works even if shell exits. forget how to do that phup or something


def _report_install_issue():
	env_debug_info = {}
	try:
		env_debug_info = debug(selected_shell=USER_SHELL)
	except Exception:
		LOGGER.debug('unexpected error getting debug info', exc_info=True)

	exc_type, exc_value, _exc_traceback = sys.exc_info()

	if isinstance(exc_value, atuin.HistoryNotFound):
		# only want to include this info when absolutley necessary: when atuin recording is not working
		env_debug_info['debug_shell_startup'] = debug_shell_startup(USER_SHELL.exec_path.as_posix())

	traceback_str = traceback.format_exc()
	payload = {
		'liminal_user_uuid': INSTALL_SESSION.liminal_user_uuid  if INSTALL_SESSION else None,
		'liminal_install_id': INSTALL_SESSION.install_id if INSTALL_SESSION else None,
		'liminal_package_version': LIMINAL_PACKAGE_VERSION,
		'exception': {
			'repr': str(exc_value),
			'exception_class': exc_type.__name__ if exc_type else None,
			'traceback': traceback_str,
		},
		'PROGRESS_TRACKER': PROGRESS_TRACKER,
		'env_debug_info': env_debug_info,
	}
	try:
		# put json in the log for easier parsing, as opposed to the dict string of it logged a few lines later
		LOGGER.debug(json.dumps(payload))
	except Exception as e:
		LOGGER.debug('Non-critical error serializing debug info', e)

	LOGGER.exception('Unexpected error during install')
	LOGGER.debug(f'sending report issue to server: {payload}')
	# TODO: with retries
	try:
		requests.post(f'{Server.API_ADDRESS}/install/issue', json=payload, timeout=10)
	except Exception as e:
		LOGGER.debug('error posting issue', stack_info=True)


def report_install_issue(exception: Exception):
	try:
		_report_install_issue()
	except Exception:
		LOGGER.exception('Exception when trying to report install issue')
		traceback.print_exc()
	if isinstance(exception, UserMessagableError):
		print(*exception.args)
	print('\n\n--------------\n')
	print(f'!!! There was an error during installation !!!')
	print(f'Please copy all the text output that comes from running the command listed below, and send it in an email to {EMAIL_CONTACT}:')
	print(f'\n\tcat {INSTALL_LOG_PATH}\n')

if __name__ == '__main__':
	main()

import logging
import os
from pathlib import Path
import subprocess
import sys
import time
import pexpect
import uuid
from liminal.logging import LOGGER


class PS1ParseException(Exception):
	pass

def _create_and_match_prompt(process: pexpect.spawn, timeout_seconds=5) -> str:
	LOGGER.debug(f'waiting for shell to startup')
	# wait for there to be no more changing output
	last_content = None
	iter_time = 0.1
	max_iterations = timeout_seconds / iter_time
	i = 0

	while i < max_iterations:
		i += 1
		time.sleep(iter_time)
		try:
			content = process.read_nonblocking(size=1024, timeout=1)
		except pexpect.TIMEOUT:
			# this seems to be ok, it fails to read a new character, so output is done
			break
		if content == last_content:
			break
		last_content = content
	LOGGER.debug(f'waited for {i}/{max_iterations}')
	return

	# shell is done starting up, we can send a command now
	uniquePS1 = f'_lm_{uuid.uuid4()}_prompt__'
	# we can have `unset PROMPT_COMMAND && ` here which will pass the preflight,
	# but it will fail once we install atuin because it (bashpre-exec) uses it
	export_command = f"export TERM=dumb && export PS1={uniquePS1}   "
	# export_command = f"export PS1={uniquePS1}   "
	LOGGER.debug(f'trying to match PS1')

	process.sendline(export_command)
	try:
		process.expect(f'export PS1={uniquePS1}   .*{uniquePS1}', timeout=2)
		LOGGER.debug(f'sucessfully set {uniquePS1=}')
		return uniquePS1
	except pexpect.TIMEOUT:
		raise PS1ParseException(f'Couldnt run login command due to unexpected PS1 parsing issue. {process.before=} {process.after=}')


TEST_COMMAND_PREFIX = 'logger "liminal_test'

def run_test_login_command(shell_exec_path: str | Path, key: str) -> str:
	full_cmd = f'{TEST_COMMAND_PREFIX} {key}"'
	output = run_login_command(str(shell_exec_path), full_cmd, log_message_prefix='Running test command\n\t$ ')
	LOGGER.debug(f'output={output}')
	return full_cmd

def debug_shell_startup(shell_exec_path: str,) -> str | None:
	try:
		child = pexpect.spawn(
			f'{shell_exec_path} -x -l', encoding='utf-8', dimensions=(111, 444), 
			# env={'PS4': '+lmdebug+'},
			timeout=6,
		)
		time.sleep(3)
		output = child.read_nonblocking(size=1024, timeout=2)
		LOGGER.debug(f'shell startup output:\n{output}')
		return output
	except Exception as e:
		LOGGER.debug('failed to get shell startup output', exc_info=True)


def run_login_command(shell_exec_path: str, cmd: str, timeout_seconds=3, log_message_prefix=''):
	"""
	this seems to be the only way to run a command from python and have atuin record it

	since someone's PS1 can contain anything and/or be dynamic (like mine), we temporarily set PS1 as a uuid we generate
	so we can match between them to get the exact command output
	
	subprocess.run(['bash', '-ic', 'mycommand; exit']) doesnt work
		# resp = subprocess.run(['bash', '-ic', f'logger "liminal installed {datetime_utcnow()} {uuid4()}"'])
		resp = subprocess.run(['bash', '-ic', f'eval "$(atuin init bash)"; echo pleaseeee; true; exit 0'], cwd=Path(__file__).parent.parent, env=None)

	other potential strategies: 
		- send noop, diff before and after content to determine PS1
		- check if there is a way to do it with `-c` and still get atuin to work, maybe just needs proper env vars
	"""

	shell_command = f"{shell_exec_path} -l"
	LOGGER.info(f"{log_message_prefix}{shell_exec_path} -l '{cmd}'", stacklevel=2)
	
	child = pexpect.spawn(
		shell_command,
		encoding='utf-8', timeout=5+2+timeout_seconds+1,
		# maxread=1,
		echo=False,
		dimensions=(111, 444) # WARNING: this is important, if not large enough, text will be truncated, causing matches to fail
	)
	# child.delaybeforesend = 0.1 # maybe this will help with unexpected timeouts/matches
	# child.logfile = sys.stdout # use sys.stdout to more easily debug (see output as it is occuring)

	try:
		_create_and_match_prompt(child, timeout_seconds=5)
	except pexpect.TIMEOUT:
		LOGGER.error('Shell startup exceeded timeout')
		raise

	try:
		# now we can match our newly set prompt
		child.sendline(cmd)
		try:
			_ = child.read_nonblocking(size=1024, timeout=timeout_seconds)
		except pexpect.TIMEOUT:
			# this seems to be ok, it fails to read a new character, so output is done
			pass
		time.sleep(timeout_seconds) # TODO: child.read_nonblocking doesn't do anything with echo=False
		raw_cmd_output = child.before
		return raw_cmd_output
	finally:
		child.terminate()
		child.close()


def run_command(cmd: list, cmd_output_log_level=logging.DEBUG, logger=LOGGER, check=True, **kwargs) -> subprocess.CompletedProcess[str]:
	logger.debug(f'Running command: {cmd}', stacklevel=2)
	try:
		task = subprocess.run(cmd, capture_output=True, text=True, check=check, **kwargs)
	except subprocess.CalledProcessError as e:
		logger.error(f'Error running command: {cmd}')
		logger.info(e.stdout)
		logger.info(e.stderr)
		raise e

	logger.log(cmd_output_log_level, task.stdout)
	logger.log(cmd_output_log_level, task.stderr)


	if task.returncode != 0:
		msg = f'Error running command: {task.returncode}: {cmd}'
		log_level = logging.WARNING
		if not check:
			log_level = logging.DEBUG
		logger.log(log_level, msg)
		logger.debug(task.stdout)
		logger.debug(task.stderr)
	else:
		logger.debug(f'Finished command: {cmd}')

	return task


if __name__ == '__main__':
	import sys
	from liminal.shell import Shell
	try:
		timeout = int(sys.argv[2])
	except (IndexError, TypeError, ValueError):
		timeout=3
	# TODO: we need to set a different LOGGER here
	output = run_login_command(Shell().exec_path.as_posix(), sys.argv[1], timeout_seconds=timeout)
	print(output)

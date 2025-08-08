
import os
from pathlib import Path
import pwd
import subprocess
import sys
import psutil

from liminal import LIMINAL_PACKAGE_VERSION, config
from liminal.datetime_util import datetime_utcnow
from liminal.filesystem import existing_path_metadata
from liminal.logging import LOGGER


class Shell:
	# we want atuin to be loaded always, so we use rc instead of profiles
	_BASH_RC = '.bashrc'
	_ZSH_RC = '.zshrc'

	_BASH_USER_CONFIG_FILES = ['.bash_profile', '.bashrc', '.bash_login', '.profile']
	_ZSH_USER_CONFIG_FILES = ['.zshrc', '.zshenv', '.zprofile']


	def __init__(self, exec_path: Path | None = None, assert_config=False):
		if not exec_path:
			self.exec_path = self.get_default_shell_path()
		else:
			self.exec_path = exec_path
		_config_file_name = self._BASH_RC if self.is_bash() else self._ZSH_RC
		self.config_file = Path.home() / _config_file_name
		self.history_file = Path.home() / '.bash_history' if self.is_bash() else Path.home() / '.zsh_history'
		# TODO: ? if history file is empty, might be good to confirm with user (we might have miss configured)

	def _envvar(self, name: str) -> str | None:
		return os.environ.get(name)
	
	def _envvar_dict(self, names: list[str]) -> dict[str, str | None]:
		result = {}
		for name in names:
			result[name] = self._envvar(name)
		return result

	def is_ssh_session(self) -> bool:
		return self._envvar('SSH_CONNECTION') is not None \
			or self._envvar('SSH_CLIENT') is not None


	def debug_config_files(self) -> dict[str, dict]:
		# FUTURE: TODO: clean-code: polymorphism once we add another shell beyond bash+zsh
		possible_config_files = self._BASH_USER_CONFIG_FILES if self.is_bash else self._ZSH_USER_CONFIG_FILES
		found_configs = {} 
		for filename in possible_config_files:
			path = Path.home() / filename
			if path.exists() and path.is_file():
				found_configs[path.as_posix()] = existing_path_metadata(path)
		return found_configs


	def dict(self):
		return {
			'name': self.exec_path.name,
			'exec_path': self.exec_path.as_posix(),
			'version': subprocess.run([self.exec_path, '--version'], check=False, capture_output=True, text=True, timeout=1).stdout,
			'envvar': self._envvar_dict([
				'SHLVL', 'TERM', 'HOME',
				'PS1',
				'PROMPT_COMMAND', 'RPROMPT', 'PROMPT_SUBST',
				'TERM_PROGRAM', 'SSH_TTY',
				'TMUX', 'BASH_ENV',
	 		]),
			'default': self.get_default_shell_path().as_posix(),
			'current': self.this_process_shell_path().as_posix(),
			'is_atty': sys.stdout.isatty(),
			'is_ssh_session': self.is_ssh_session(),
			'existing_configs': self.debug_config_files(),
		}


	def _bash_config_creation(self):
		"""it isn't guaranteed that a bashrc file exists (i guess?)
		so this will create the necessary files to have and load a bashrc
		"""
		if self.is_bash() and not self.config_file.exists():
			LOGGER.info('Creating ~/.bashrc')
			self.config_file.touch()

			profile = Path.home() / '.bash_profile'
			if not profile.exists():
				# this should never happen right? or i guess they could be using .profile?
				LOGGER.info(f'Creating ~/{profile.name}')
				profile.touch()

			profile_content = profile.read_text()
			if '.bashrc' in profile_content:
				# assuming any mention of .bashrc means it is being sourced properly
				# if needed, we can validate this more (if it is commented out)
				return
			
			LOGGER.info('Adding block in ~/.bash_profile to load ~/.bashrc')

			source_bashrc_block = f"""
### Liminal tools ---
# version {LIMINAL_PACKAGE_VERSION}. date = {datetime_utcnow()}
if [ -f ~/.bashrc ];
  then source ~/.bashrc
fi
### --- Liminal tools
"""
			profile.write_text(source_bashrc_block)


	def is_config_writable(self):
		return os.access(self.config_file, os.W_OK)	

	@classmethod
	def is_supported_exe_path(cls, path: str | Path):
		return Path(path).name in ['bash', 'zsh']

	def is_supported(self):
		return self.is_supported_exe_path(self.exec_path)
	
	def is_bash(self):
		return self.exec_path.name == 'bash'

	def get_default_shell_path(self) -> Path:
		"""Gets the default shell for the current user."""
		# NOTE: we also have shellingham installed (dependency of typer)
		user_id = os.getuid()
		user_info = pwd.getpwuid(user_id)
		return Path(user_info.pw_shell)
		
	def this_process_shell_path(self) -> Path:
		parent_pid = os.getppid()
		parent_process = psutil.Process(parent_pid)
		# .exe() gives the full path, .name() just the command name (e.g., 'bash')
		# We prefer .exe() for uniqueness
		shell_exe = parent_process.exe()
		return Path(shell_exe)
	

	def try_parse_login_command(self):
		from liminal.command_runner import run_test_login_command, PS1ParseException
		import uuid
		key = str(uuid.uuid4())
		try:
			output = run_test_login_command(self.exec_path.as_posix(), key)
		except PS1ParseException as e:
			raise e
		# TODO: search syslog
		# assert output and key in output, f'Did not find {key=} in {output=}'


def path_replace_home_with_var(path: Path) -> str:
	_path = path.expanduser()
	
	if _path.is_relative_to(Path.home()):
		_path = '$HOME' / _path.relative_to(Path.home())

	return _path.as_posix()


def determine_shell(on_conflict_ask_user=True) -> Shell:
	"""get the shell obj for a user. prompts them to specifiy shell if there is an unexpected difference"""

	default_shell = Shell()
	current_shell_path = default_shell.this_process_shell_path().resolve()
	default_shell_path = default_shell.get_default_shell_path().resolve()

	# if one of the shells isn't supported (ex: docker will get `bash` and `dash`), return the other
	# if both arent supported, it will error out a bit later
	if not Shell.is_supported_exe_path(default_shell_path):
		LOGGER.debug(f'not supported: {default_shell_path=}, selecting {current_shell_path}')
		return Shell(exec_path=current_shell_path)
	if not Shell.is_supported_exe_path(current_shell_path):
		LOGGER.debug(f'not supported: {current_shell_path=}, selecting {default_shell_path}')
		return Shell(exec_path=default_shell_path)
	
	if current_shell_path == default_shell_path:
		return default_shell
	
	LOGGER.debug(f'Shell paths differ: {default_shell_path=} {current_shell_path=}')
	
	if path := config.Config.LIMINAL_INSTALLER_SHELL_PATH:
		return Shell(exec_path=Path(path))
	
	if not on_conflict_ask_user:
		return Shell(exec_path=current_shell_path)

	from rich.prompt import IntPrompt
	from rich.console import Console

	console = Console()
	console.print(f'Your default shell is [italic]{default_shell_path}[/], but your current shell is [italic]{current_shell_path}[/]')
	console.print("[bold]Which would you like to use?")
	
	shell_choices=[default_shell_path.as_posix(), current_shell_path.as_posix(),]

	for i, choice in enumerate(shell_choices):
		msg = f'  [cyan]{i+1}[/cyan]. {choice}'
		if i == 0:
			msg += f'   [italic](default)'
		console.print(msg)

	console.print("[italic](If you're not sure, choose default (1))[/]")
	selection_idx = IntPrompt.ask(
		'Enter the number of your choice',
		choices=[str(i+1) for i in range(len(shell_choices))],
		# default=default_index+1, # no default so user has to type instead of just press enter (ive done too hasty of an enter many times)
		show_choices=False, # i think =True is more confusing to casual users
	)
	selected_shell_path = shell_choices[selection_idx - 1]
	LOGGER.debug(f'user {selected_shell_path=}')
	return Shell(exec_path=Path(selected_shell_path))


if __name__ == '__main__':
	s = determine_shell()


import json
import logging
from pathlib import Path
from typing import Annotated
import uuid
import requests
import typer
from liminal import atuin
from liminal.command_runner import run_command
from liminal.env import datetime_utcnow
from liminal.installer import main
from liminal.config import Config
from liminal.session import InstallationSession

app = typer.Typer(name='shell')

@app.command()
def install():
	main()


# TODO:
def onboarding():
	pass


@app.command()
def sync(install_id: Annotated[str | None, typer.Option()] = None):
	# --notify
	print(datetime_utcnow(), install_id)
	session = InstallationSession.load_most_recent()
	if session.api_address != Config.API_ADDRESS:
		# uhoh
		pass
	run_command([atuin.Paths.EXECUTABLE, 'sync'], 
			 env={'ATUIN_SESSION': str(uuid.uuid4()).replace('-', ''), 'HOME': Path.home()},
			 cmd_output_log_level=logging.ERROR,
			 check=False, # TODO: why am i getting error code when it syncs good?
	)
	print(datetime_utcnow())

	host_id = atuin.get_host_id()
	payload = {
		'host_id': host_id,
	}
	headers = {'Authorization': f'Bearer {session.cli_api_access_token}'}
	resp = requests.post(f'{Config.API_ADDRESS}/sync/initial', json=payload, timeout=10, headers=headers)
	print(json.dumps(resp.json(), indent=2))


# def set_auth_key():
# 	# typer.prompt()
# 	key = input('Your key from the liminal site: ')
# 	(config_dir / 'shell_sync_token').write_text(key)


def info():
	# details of last recorded atuin command, in particular the timestamp
	pass



# TODO:
def repro():
	"""
	package up your terminal into a dump we can try and reproduce issues with

	please remove any senstive info you wish we dont see (we will delete your package after replicating and resolving your issue)
	
	
	- rc files
	- history files
	
	"""

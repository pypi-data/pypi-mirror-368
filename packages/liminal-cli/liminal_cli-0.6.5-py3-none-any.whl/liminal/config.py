import os

from liminal import LIMINAL_DIR

class Config:
	HOST = os.environ.get('LIMINAL_SHELLSYNC_HOST', 'shellsync.liminalbios.com')
	API_ADDRESS = os.environ.get('LIMINAL_SHELLSYNC_APP_ADDRESS', f'https://{HOST}/api/v1').rstrip('/')
	ATUIN_SYNC_ADDRESS = os.environ.get('LIMINAL_SHELLSYNC_ATUIN_ADDRESS', f'https://atuin.services.{HOST}').rstrip('/')

	LIMINAL_INSTALLER_SKIP_CLEANUP = os.environ.get('LIMINAL_INSTALLER_SKIP_CLEANUP', 'no').strip().lower()
	LIMINAL_INSTALLER_SKIP_ATUIN_IMPORT_HISTORY = os.environ.get('LIMINAL_INSTALLER_SKIP_ATUIN_IMPORT', None)
	LIMINAL_INSTALLER_PAUSE_AT = os.environ.get('LIMINAL_INSTALLER_PAUSE_AT', '').strip()
	LIMINAL_INSTALLER_ATUIN_HISTORY_SEED_FILE = os.environ.get('LIMINAL_INSTALLER_ATUIN_HISTORY_SEED_FILE', None)
	LIMINAL_INSTALLER_SHELL_PATH = os.environ.get('LIMINAL_INSTALLER_SHELL_PATH', None) # '/bin/bash', '/bin/zsh'


class Paths:
	SESSION_RECEIPTS_FILE = LIMINAL_DIR / 'session.jsonl'



"""

store the install_id+token so we can verify the user did a previous install even if they aren't logged in to atuin
because `atuin status` will fail if the database doesn't contain their session anymore (which could occur if we are cleaning up the db trying to reset a failed install)

"""

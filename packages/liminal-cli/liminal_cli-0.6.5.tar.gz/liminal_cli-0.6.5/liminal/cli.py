from typing import Annotated
import typer

from .commands import shell
from . import LIMINAL_PACKAGE_VERSION

app = typer.Typer(pretty_exceptions_enable=False)

app.add_typer(shell.app, )


@app.command()
def info(debug: bool = False):
	from . import env
	import json

	print('Liminal\'s ShellSync is powered by atuin: https://atuin.sh/')
	# https://deepwiki.com/atuinsh/atuin/5.2-security-and-privacy

	# last sync
	# atuin docs link

	# --status (syncing progress for large historys)
	# install status ()

	# --debug
	if debug:
		print(json.dumps(env.debug(), indent='\t'))
	# try `atuin sync`, ping our server
	# search our logs for any issues 
	# num install attempts (determined from logs)


	# shellextension
	# we read these Externally defined environment variables
	# $HOME



# or doctor?
def triage():
	# try to fix the issue for the user, and if all fails, then prints debug/info
	pass
	# troubleshoot

# @app.command()
# def prompt_upgrade():
# 	input('Would you like to upgrade from Liminal v{} to v{}?')


def upgrade():
	# https://docs.astral.sh/uv/concepts/tools/#upgrading-tools
	command = [
            "uv", "tool", "upgrade", "liminal_cl",
            "--upgrade-package", "liminal-cli",
        ]
	# ????
	# --python {sys.executable}


@app.command()
def install():
	from liminal import installer
	installer.main()


@app.command()
def self():
	# backup, clean, uninstall
	"""
	# uninstall
	cp .local/share/atuin/history.db ./my-backed-up-atuin-history.db
	## remove all
	rm -rf .atuin/ .local/share/atuin/ .config/atuin ; rm -rf .liminal-tools/ ; rm lminstall.py
	## remove so can run from `.liminal-tools/venv/bin/python -m liminal.cli install`
	rm -rf .atuin/ .local/share/atuin/ .config/atuin 

	# manual: if installed atuin standalone (without us) previously, remove the sourceing of atuin in whatever rc file


	export LIMINAL_INSTALLER_SKIP_ATUIN_IMPORT=True && export LIMINAL_INSTALLER_PAUSE_AT=installed_atuin && export LIMINAL_INSTALLER_SKIP_CLEANUP=yes
	curl -f https://shellsync.liminalbios.com/api/v1/install > ~/lminstall.py && python3 ~/lminstall.py

	# the `rm` seems to be necessary, otherwise the copied db wont work
	rm ~/.local/share/atuin/history.db* && cp my-backed-up-atuin-history.db ~/.local/share/atuin/history.db

	
	# load debug
	source .debug.env file
	liminal-python: .local/share/uv/tools/liminal-cli/bin/python
	"""
	pass


# help, --help, -h # allow `help` since might be easier to remember for those who dont know the standard flag
# --help --beginner --onboarding
# this is the liminal_cl tool, which blah blah blah
# some common things you might want to do:
# x,y,z
# if you have any further questions, reach out to us at @aemail.com

@app.command(name='help')
def help_command(
	ctx: typer.Context,
	lastname: Annotated[str, typer.Option(help="this option does this and that")] = ""
):
	"""
	alias for --help.
	"""
	main_app_ctx = ctx.parent
	help_text = main_app_ctx.get_help()
	print(help_text)
	raise typer.Exit()
	


def version_callback(value: bool):
	if value:
		print(LIMINAL_PACKAGE_VERSION)
		raise typer.Exit()


@app.callback()
def common(
	ctx: typer.Context,
	version: bool = typer.Option(None, "--version", callback=version_callback)
):
	pass

if __name__ == '__main__':
	app()


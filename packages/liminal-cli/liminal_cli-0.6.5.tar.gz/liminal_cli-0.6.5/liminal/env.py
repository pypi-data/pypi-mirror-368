import getpass
import json
import os
import platform
import socket
import subprocess
import sys


from liminal import LIMINAL_DIR
from liminal import config, atuin, shell
from liminal.datetime_util import datetime_utcnow

LAST_SUCCESS_INSTALL_FLAG_PATH = LIMINAL_DIR / 'install-successful'



def _run_command(command_parts, timeout=3):
	"""
	Helper function to run a shell command and return its output.
	Returns (stdout, stderr, return_code)
	"""
	try:
		process = subprocess.run(
			command_parts,
			capture_output=True,
			text=True,
			timeout=timeout,
			check=False  # Don't raise exception for non-zero exit codes
		)
		return process.stdout.strip(), process.stderr.strip(), process.returncode
	except FileNotFoundError:
		return f"Error: Command '{command_parts[0]}' not found.", "", -1
	except subprocess.TimeoutExpired:
		return f"Error: Command '{' '.join(command_parts)}' timed out after {timeout}s.", "", -2
	except Exception as e:
		return f"Error running '{' '.join(command_parts)}': {str(e)}", "", -3


def get_os_distro_info() -> dict[str, str]:
	os_distro = {}
	# Try /etc/os-release (standard for modern distros)
	try:
		with open("/etc/os-release", "r") as f:
			for line in f:
				line = line.strip()
				if not line or line.startswith("#") or "=" not in line:
					continue
				key, value = line.split("=", 1)
				# Remove quotes from value if present
				value = value.strip('"')
				os_distro[f"os_release_{key.lower()}"] = value
	except FileNotFoundError:
		os_distro["os_release_file"] = "Not found (/etc/os-release)"
	except Exception as e:
		os_distro["os_release_file_error"] = str(e)

	# Try lsb_release command (common but not always present)
	if not os_distro.get("os_release_pretty_name"): # If /etc/os-release didn't give a good name
		lsb_out, lsb_err, lsb_ret = _run_command(["lsb_release", "-a"])
		if lsb_ret == 0 and lsb_out:
			for line in lsb_out.splitlines():
				if ":" in line:
					key, value = line.split(":", 1)
					os_distro[f"lsb_{key.strip().lower().replace(' ', '_')}"] = value.strip()
		elif lsb_ret == -1: # Command not found
			os_distro["lsb_release_command"] = "Not found"
		elif lsb_err:
			os_distro["lsb_release_error"] = lsb_err

	# Fallback: /etc/issue (less structured)
	if not os_distro.get("os_release_pretty_name") and not os_distro.get("lsb_distributor_id"):
		try:
			with open("/etc/issue", "r") as f:
				os_distro["etc_issue"] = f.read().strip()
		except FileNotFoundError:
			os_distro["etc_issue_file"] = "Not found (/etc/issue)"
		except Exception as e:
			os_distro["etc_issue_file_error"] = str(e)
	return os_distro

def get_linux_debug_info():
	"""
	Gathers various pieces of debug information from a Linux/Unix system.
	Returns a dictionary of debug information.
	"""
	info = {}

	# --- Basic System Information ---
	info["python_version"] = sys.version
	info["python_executable"] = sys.executable
	info["platform_system"] = platform.system()
	info["platform_release"] = platform.release()
	info["platform_version"] = platform.version()
	info["platform_machine"] = platform.machine()
	info["platform_node"] = platform.node() # hostname
	info["platform_uname"] = str(platform.uname())

	info["os_distribution"] = get_os_distro_info()

	# --- Kernel Information ---
	kernel_info = {}
	uname_r, _, ret = _run_command(["uname", "-r"]) # Kernel release
	if ret == 0: kernel_info["kernel_release"] = uname_r
	uname_v, _, ret = _run_command(["uname", "-v"]) # Kernel version
	if ret == 0: kernel_info["kernel_version"] = uname_v
	uname_a, _, ret = _run_command(["uname", "-a"]) # All kernel info
	if ret == 0: kernel_info["kernel_all"] = uname_a
	info["kernel_info"] = kernel_info
	
	   # --- Network Information ---
	network_info = {}
	try:
		network_info["hostname"] = socket.gethostname()
		network_info["fqdn"] = socket.getfqdn()
		# Note: socket.gethostbyname can be slow or fail if DNS isn't perfect
		try:
			network_info["ip_address_via_socket"] = socket.gethostbyname(network_info["hostname"])
		except socket.gaierror:
			network_info["ip_address_via_socket"] = "Could not resolve hostname to IP"
	except Exception as e:
		network_info["socket_error"] = str(e)


	# --- User and Environment ---
	user_env_info = {}
	user_env_info["current_user"] = os.getenv("USER", "N/A")
	user_env_info["effective_uid"] = os.geteuid()
	user_env_info["effective_gid"] = os.getegid()
	
	id_out, id_err, id_ret = _run_command(["id"])
	if id_ret == 0: user_env_info["id_command"] = id_out
	else: user_env_info["id_command_error"] = id_err if id_err else "Command failed or not found"

	user_env_info["path_env_var"] = os.getenv("PATH", "N/A")
	user_env_info["home_env_var"] = os.getenv("HOME", "N/A")
	user_env_info["lang_env_var"] = os.getenv("LANG", "N/A")
	user_env_info["locale_output"] = _run_command(["locale"])[0] # Get first element (stdout)
	info["user_environment"] = user_env_info


	return info





def debug(selected_shell: shell.Shell | None = None):
	"""
	which shells are available. /etc/shells

	if all expected atuin files/dirs exist, and their mod times

	"""
	# python -m site
	dt = datetime_utcnow()

	last_install = None
	if LAST_SUCCESS_INSTALL_FLAG_PATH.exists():
		last_install = LAST_SUCCESS_INSTALL_FLAG_PATH.read_text()

	try:
		sessions = json.loads(config.Paths.SESSION_RECEIPTS_FILE.read_text())
	except Exception:
		sessions = None

	if not selected_shell:
		selected_shell = shell.Shell()

	return {
		'datetime': dt.isoformat(),
		'datetime_local': dt.astimezone().isoformat(),
		'argv': sys.argv,
		'user': {
			'username': getpass.getuser(), 
			'uid': os.getuid(),
			'gid': os.getgid(),
		},
		'selected_shell': selected_shell.dict(),
		'info': get_linux_debug_info(),
		'python': {
			# 'pip_freeze': subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True, check=False).stdout,
			'path': sys.path
		},
		'last_sucessful_install': last_install,
		'atuin': atuin.debug_info(),
		'installer_config': {key:val for key, val in config.Config.__dict__.items() if not key.startswith('__')},
		'sessions': sessions,
	}

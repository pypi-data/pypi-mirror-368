import os
from pathlib import Path



def existing_path_metadata(path: Path) -> dict[str, str | int | float | bool]:
	return {
		'date_created': path.stat().st_ctime,
		'date_modified': path.stat().st_mtime,
		'owner': path.owner(),
		'size': path.stat().st_size,
		'is_writeable': os.access(path, os.W_OK),
	}


def path_metadata(given_path: Path, depth=1) -> dict:
	path = given_path.expanduser()
	metadata = {
		'given_path': given_path.as_posix(),
		'resolved_path': path.as_posix(),
		'exists': path.exists(),
	}

	if path.exists():
		metadata = metadata | existing_path_metadata(path)
	if path.is_dir():
		metadata['child_count'] = len(list(path.glob('*')))
		if depth > 0:
			metadata['children'] = []
			for child in path.iterdir():
				metadata['children'].append(path_metadata(child, depth=depth-1))

	return metadata

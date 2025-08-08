


import dataclasses
import json
from typing import Self

from liminal import config
from liminal.datetime_util import datetime_utcnow_iso




@dataclasses.dataclass
class InstallationSession:
	liminal_user_uuid: str
	install_id: str
	cli_api_access_token: str
	username: str

	api_address: str

	datetime_created: str = dataclasses.field(default_factory=datetime_utcnow_iso)
	# atuin_host_id: str

	def save(self):
		with config.Paths.SESSION_RECEIPTS_FILE.open(mode='+a') as f:
			f.write(json.dumps(self.__dict__)+'\n')

	@classmethod
	def load_most_recent(cls) -> Self:
		sessions = config.Paths.SESSION_RECEIPTS_FILE.read_text().splitlines()
		last_session = json.loads(sessions[-1])
		return cls(**last_session)

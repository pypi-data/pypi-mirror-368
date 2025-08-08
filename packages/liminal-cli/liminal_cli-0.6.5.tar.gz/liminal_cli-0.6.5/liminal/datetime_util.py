import datetime


def datetime_utcnow() -> datetime.datetime:
	return datetime.datetime.now(datetime.timezone.utc)

def datetime_utcnow_iso() -> str:
	return datetime_utcnow().isoformat()

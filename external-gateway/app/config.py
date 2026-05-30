from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

import logging

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
	open_meteo_url: str
	gee_credentials_file: str
	gee_project_id: str | None
	gee_collection_name: str


def _resolve_project_id(credentials_file: str) -> str | None:
	try:
		data = json.loads(Path(credentials_file).read_text(encoding="utf-8"))
	except (OSError, json.JSONDecodeError):
		return None

	return data.get("project_id")


def _validate_service_account_location(path_str: str) -> None:
	try:
		p = Path(path_str).resolve()
	except Exception:
		return

	cwd = Path.cwd().resolve()
	try:
		# If the credentials file is inside the repo/workspace, warn the user
		if cwd in p.parents or p == cwd:
			_log.warning(
				"GEE service account file appears to be inside the project workspace (%s). "
				"For security, place credentials outside the repository and add them to .gitignore.",
				cwd,
			)
	except Exception:
		# best effort only
		return


def get_settings() -> Settings:
	credentials_file = os.getenv("GEE_CREDENTIALS_FILE", "./service_account.json")
	project_id = os.getenv("GEE_PROJECT_ID") or _resolve_project_id(credentials_file)
	# warn if the credentials file is located inside the project workspace
	_validate_service_account_location(credentials_file)

	return Settings(
		open_meteo_url=os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast"),
		gee_credentials_file=credentials_file,
		gee_project_id=project_id,
		gee_collection_name=os.getenv(
			"GEE_COLLECTION_NAME", "COPERNICUS/S2_SR_HARMONIZED"
		),
	)


settings = get_settings()


# end

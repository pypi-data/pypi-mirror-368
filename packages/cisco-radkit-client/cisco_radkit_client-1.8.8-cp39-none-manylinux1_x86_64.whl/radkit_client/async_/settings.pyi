from collections.abc import Iterable
from pathlib import Path
from radkit_common.settings.client import ClientSettingsLoader as ClientSettingsLoader, UseE2EE as UseE2EE, get_client_settings as get_settings, get_client_settings_loader as get_settings_loader

__all__ = ['UseE2EE', 'ClientSettingsLoader', 'get_settings_loader', 'get_settings', 'load_settings']

def load_settings(path: Path | str | None = None, extra_settings: Iterable[tuple[str, str]] | None = None) -> None: ...

from exceptions.file_system import FileSystemException
from typing import Any
from pathlib import Path

from conf import settings
from exceptions.settings import SettingsException
from libs.singleton import SingletonMeta


class FileSystem(metaclass=SingletonMeta):
    struct_is_created = False

    def __init__(self) -> None:
        self.__dict__.update(FileSystem.get_settings_vars())

    def __is_settings_var(var: tuple[str, Any]) -> bool:
        name_var, key_var = var[0], var[1]
        return name_var.endswith(("_FILE", "_DIR"))

    def get_settings_vars() -> dict[str, Any]:
        return dict(filter(FileSystem.__is_settings_var, settings.__dict__.items()))

    def create_file_struct(self, exist_ok: bool = True) -> None:
        if not exist_ok and FileSystem.struct_is_created:
            raise FileSystemException("File struct is created")

        setting_vars = FileSystem.get_settings_vars()
        if not all(map(lambda x: isinstance(x, Path), setting_vars.values())):
            raise SettingsException(
                "_FILE and _DIR variables type should be pathlib.Path"
            )

        for value_var in setting_vars.values():
            value_var.mkdir(parents=True, exist_ok=True)
        FileSystem.struct_is_created = True

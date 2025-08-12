from typing import Optional

from wexample_config.const.types import DictConfig
from wexample_filestate.file_state_manager import FileStateManager


class Workdir(FileStateManager):
    def prepare_value(self, raw_value: Optional[DictConfig] = None) -> DictConfig:
        from wexample_wex_core.const.globals import WORKDIR_SETUP_DIR
        from wexample_filestate.const.disk import DiskItemType

        raw_value = super().prepare_value(raw_value)

        if "children" not in raw_value:
            raw_value["children"] = []

        raw_value["children"].append({
            "name": WORKDIR_SETUP_DIR,
            'type': DiskItemType.DIRECTORY,
            'should_exist': True,
        })

        return raw_value

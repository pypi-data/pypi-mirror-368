from typing import Optional

from wexample_config.const.types import DictConfig
from wexample_filestate.config_value.readme_content_config_value import ReadmeContentConfigValue
from wexample_filestate.const.disk import DiskItemType


class WithReadmeWorkdirMixin:
    def append_readme(self, config: Optional[DictConfig] = None) -> DictConfig:
        config.get("children").append({
            "name": 'README.md',
            "type": DiskItemType.FILE,
            "should_exist": True,
            "default_content": ReadmeContentConfigValue(
                templates=[],
                parameters={}
            ),
        })

        return config

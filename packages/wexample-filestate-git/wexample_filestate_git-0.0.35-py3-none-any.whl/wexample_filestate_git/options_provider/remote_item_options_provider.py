from typing import List, Type, TYPE_CHECKING

from wexample_config.config_option.name_config_option import NameConfigOption
from wexample_config.options_provider.abstract_options_provider import AbstractOptionsProvider
from wexample_filestate.config_option.type_config_option import TypeConfigOption
from wexample_filestate_git.config_option.create_remote_config_option import CreateRemoteConfigOption
from wexample_filestate_git.config_option.url_config_option import UrlConfigOption

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class RemoteItemOptionsProvider(AbstractOptionsProvider):
    @classmethod
    def get_options(cls) -> List[Type["AbstractConfigOption"]]:
        return [
            NameConfigOption,
            UrlConfigOption,
            CreateRemoteConfigOption,
            TypeConfigOption
        ]

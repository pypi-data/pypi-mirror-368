from typing import TYPE_CHECKING

from wexample_config.config_option.abstract_nested_config_option import AbstractNestedConfigOption
from wexample_filestate_git.options_provider.remote_item_options_provider import RemoteItemOptionsProvider

if TYPE_CHECKING:
    from wexample_config.options_provider.abstract_options_provider import AbstractOptionsProvider


class RemoteItemConfigOption(AbstractNestedConfigOption):
    def get_options_providers(self) -> list[type["AbstractOptionsProvider"]]:
        return [
            RemoteItemOptionsProvider
        ]

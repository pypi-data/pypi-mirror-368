from typing import List, Type, TYPE_CHECKING

from wexample_filestate.operations_provider.abstract_operations_provider import AbstractOperationsProvider

if TYPE_CHECKING:
    from wexample_filestate.operation.abstract_operation import AbstractOperation


class GitOperationsProvider(AbstractOperationsProvider):
    @staticmethod
    def get_operations() -> List[Type["AbstractOperation"]]:
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation
        from wexample_filestate_git.operation.git_remote_add_operation import GitRemoteAddOperation
        from wexample_filestate_git.operation.git_remote_create_operation import GitRemoteCreateOperation
        from wexample_filestate.const.state_items import TargetFileOrDirectory
        from wexample_helpers.helpers.polyfill import polyfill_import

        polyfill_import(TargetFileOrDirectory)

        GitRemoteAddOperation.model_rebuild()
        GitRemoteCreateOperation.model_rebuild()

        return [
            GitInitOperation,
            GitRemoteAddOperation,
            GitRemoteCreateOperation,
        ]

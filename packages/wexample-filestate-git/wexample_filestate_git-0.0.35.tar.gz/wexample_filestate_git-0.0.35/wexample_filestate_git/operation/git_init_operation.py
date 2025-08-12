from __future__ import annotations

from typing import TYPE_CHECKING, List, Type

from git import Repo

from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.file_create_operation import FileCreateOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import FileManipulationOperationMixin
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_helpers.const.globals import DIR_GIT

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_filestate_git.config_option.abstract_config_option import AbstractConfigOption


class GitInitOperation(FileManipulationOperationMixin, AbstractGitOperation):
    _original_path_str: str
    _has_initialized_git: bool = False

    def dependencies(self) -> List[Type["AbstractOperation"]]:
        return [
            FileCreateOperation
        ]

    @staticmethod
    def applicable_option(target: TargetFileOrDirectoryType, option: "AbstractConfigOption") -> bool:
        from wexample_filestate_git.config_option.git_config_option import GitConfigOption
        from wexample_helpers_git.helpers.git import git_is_init

        if isinstance(option, GitConfigOption):
            return option.should_have_git() and not git_is_init(target.get_path())

        return False

    def describe_before(self) -> str:
        return 'No initialized .git directory'

    def describe_after(self) -> str:
        return 'Initialized .git directory'

    def description(self) -> str:
        return 'Initialize .git directory'

    def apply(self) -> None:
        path = self._get_target_file_path(target=self.target)
        self._has_initialized_git = True

        repo = Repo.init(path)
        repo.init()

    def undo(self) -> None:
        import shutil

        if self._has_initialized_git:
            shutil.rmtree(self._get_target_file_path(target=self.target) + DIR_GIT)

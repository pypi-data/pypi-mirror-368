from typing import Optional

from tidipy.composer_repository import ComposerRepository
from tidipy.scope import Scope
from tidipy.scope_context import ScopeContext
from tidipy.scope_type import RootType


class RootScopeProvider:
    _root_scope: Optional[Scope] = None

    @classmethod
    def get(cls) -> Scope:
        if cls._root_scope is None:
            RootScopeProvider._root_scope = Scope(
                scope_id='root',
                scope_type=RootType(),
                composers=ComposerRepository.get_composers(),
                context=ScopeContext.empty()
            )

        return cls._root_scope

    @classmethod
    def reset(cls) -> None:
        cls._root_scope = None

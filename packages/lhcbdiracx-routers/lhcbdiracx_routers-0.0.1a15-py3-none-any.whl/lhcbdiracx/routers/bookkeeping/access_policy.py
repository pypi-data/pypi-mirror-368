"""
Bookkeeping AccessPolicy
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum, auto
from typing import Annotated

from diracx.routers.access_policies import BaseAccessPolicy
from diracx.routers.utils.users import AuthorizedUserInfo
from fastapi import Depends


class ActionType(StrEnum):
    HELLO = auto()

    READ = auto()

    WRITE = auto()


class BookkeepingAccessPolicy(BaseAccessPolicy):

    @staticmethod
    async def policy(
        policy_name: str,
        user_info: AuthorizedUserInfo,
        /,
        *,
        action: ActionType | None = None,
        **kwargs,
    ):
        assert action, "action is a mandatory parameter"

        assert action in [
            ActionType.HELLO,
            ActionType.READ,
        ], "Only HELLO and READ actions are allowed"

        return


CheckBookkeepingPolicyCallable = Annotated[
    Callable, Depends(BookkeepingAccessPolicy.check)
]

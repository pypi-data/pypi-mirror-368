"""Stress test endpoints to ensure the system can scale."""

from __future__ import annotations

import asyncio
import random
from datetime import timedelta
from uuid import uuid4

from diracx.core.models import AccessTokenPayload, RefreshTokenPayload, TokenResponse
from diracx.logic.auth.token import create_token, insert_refresh_token
from diracx.routers.access_policies import open_access
from diracx.routers.dependencies import AuthDB
from diracx.routers.fastapi_classes import DiracxRouter
from diracx.routers.utils.users import AuthSettings

router = DiracxRouter(require_auth=False)


@open_access
@router.get("/ping")
async def ping(
    delay: float = 0,
) -> dict[str, str | float]:
    """Ping the server adding a random sleep in the process.

    This endpoint is used to assess the server's responsiveness.
    It has been developed to stress test the server.
    """
    # Wait for a random time between 0 and 5 seconds
    if delay and delay <= 1:
        wait = delay
    else:
        wait = random.uniform(0, 1)  # noqa: S311
    await asyncio.sleep(wait)
    return {"message": "pong", "delay": wait}


@open_access
@router.get("/token")
async def token(
    auth_db: AuthDB,
    settings: AuthSettings,
    pilot_uuid: str = "",
) -> TokenResponse:
    """Mint dummy refresh and access tokens for pilots.
    The tokens should not have any property and should be useless,
    they just exist to stress test the server.
    """
    # Generate a random subject & preferred_username
    vo = "lhcb"
    sub = f"{vo}:pilot{pilot_uuid}"
    preferred_username = f"Maverick_{pilot_uuid}"

    # Insert the refresh token with user details into the RefreshTokens table
    # User details are needed to regenerate access tokens later
    jti, creation_time = await insert_refresh_token(
        auth_db=auth_db,
        subject=sub,
        preferred_username=preferred_username,
        scope="",
    )

    # Generate refresh token payload
    refresh_payload: RefreshTokenPayload = {
        "jti": str(jti),
        "exp": creation_time + timedelta(minutes=settings.refresh_token_expire_minutes),
        # refresh token was not obtained from the legacy_exchange endpoint
        "legacy_exchange": False,
        "dirac_policies": {},
    }

    # Generate access token payload
    # For now, the access token is only used to access DIRAC services,
    # therefore, the audience is not set and checked
    access_payload: AccessTokenPayload = {
        "sub": sub,
        "vo": vo,
        "iss": settings.token_issuer,
        "dirac_properties": [],
        "jti": str(uuid4()),
        "preferred_username": preferred_username,
        "dirac_group": "lhcb_pilot",
        "exp": creation_time + timedelta(minutes=settings.access_token_expire_minutes),
        "dirac_policies": {},
    }

    access_token = create_token(access_payload, settings)
    refresh_token = create_token(refresh_payload, settings)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_token=refresh_token,
    )

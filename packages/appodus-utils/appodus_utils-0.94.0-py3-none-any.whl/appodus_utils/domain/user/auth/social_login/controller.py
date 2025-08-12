from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from kink import di

from appodus_utils import Utils
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.domain.user.auth.models import SocialAuthOperationType, OAuthCallbackRequest
from appodus_utils.domain.user.auth.service import AuthService
from appodus_utils.domain.user.auth.social_login.factory import SocialAuthProviderFactory
from appodus_utils.domain.user.auth.social_login.interface import ISocialAuthProvider

SOCIAL_LOGIN_CALLBACK_PATH = Utils.get_from_env_fail_if_not_exists("SOCIAL_LOGIN_CALLBACK_PATH")

social_auth_router = APIRouter(prefix=SOCIAL_LOGIN_CALLBACK_PATH)
social_auth_service_factory: SocialAuthProviderFactory = di[SocialAuthProviderFactory]
auth_service:AuthService = di[AuthService]


@social_auth_router.post("/{provider}")
async def auth_callback(provider: str, request: Request, code: str = None, state: str = None):
    # Verify state
    stored_state = await RedisUtils.get_redis(state)
    if not stored_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Get stored code_verifier
    code_verifier = stored_state.get("code_verifier")
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Missing code_verifier")


    operation_type = stored_state.get("operation_type")
    auth_provider = social_auth_service_factory.get_auth_provider(provider)

    try:
        payload = OAuthCallbackRequest(code=code, code_verifier=code_verifier, operation_type=operation_type)
        userinfo = await auth_provider.verify(payload, request)

        return await auth_service.social_login_signup(userinfo)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@social_auth_router.get("/{provider}/init")
async def init_social_auth(provider: str, operation_type: SocialAuthOperationType, request: Request):
    auth_provider: ISocialAuthProvider = social_auth_service_factory.get_auth_provider(provider)

    try:
        response = await auth_provider.initialize(operation_type, request)
        return {"redirectUrl": response["url"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

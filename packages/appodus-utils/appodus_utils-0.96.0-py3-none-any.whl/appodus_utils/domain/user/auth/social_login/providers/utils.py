import urllib.parse
from logging import Logger

from kink import di
from starlette.requests import Request

from appodus_utils import Utils
from appodus_utils.common.auth_utils import JwtAuthUtils
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.domain.user.auth.models import SocialAuthOperationType
from appodus_utils.domain.user.auth.social_login.models import SocialAuthPlatform

logger: Logger = di["logger"]


@decorate_all_methods(method_trace_logger, exclude=['__init__'], exclude_startswith='_')
class OauthUtils:

    @staticmethod
    async def init_0auth(request: Request, base_url: str, client_id: str, redirect_uri: str, scope: str, operation_type: SocialAuthOperationType) -> dict:
        code_challenge, code_verifier, state = JwtAuthUtils.generate_pkce()

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        await RedisUtils.set_redis(state, {code_verifier: code_verifier, operation_type: operation_type})

        query_string = urllib.parse.urlencode(params)
        return {
            "url": f"{base_url}?{query_string}",
            "code_verifier": code_verifier
        }

    @staticmethod
    async def get_auth_redirect_url(platform: SocialAuthPlatform, request: Request) -> str:
        base_url = str(request.base_url)  # e.g., https://yourdomain.com/
        AUTH_URL_PATH = Utils.get_from_env_fail_if_not_exists("AUTH_URL_PATH")
        SOCIAL_LOGIN_CALLBACK_PATH = Utils.get_from_env_fail_if_not_exists("SOCIAL_LOGIN_CALLBACK_PATH")
        redirect_path = f"{AUTH_URL_PATH}{SOCIAL_LOGIN_CALLBACK_PATH}/{platform.value}"

        full_url = urllib.parse.urljoin(base_url, redirect_path)

        return full_url

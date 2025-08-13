from fastapi import APIRouter



from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils import RouterUtils
from appodus_utils.domain.key_value.models import KeyValue
from appodus_utils.domain.user.controller import user_router

utils_router = APIRouter(prefix="/v1", tags=["Utils"])

RouterUtils.add_routers(utils_router, [
    user_router
])
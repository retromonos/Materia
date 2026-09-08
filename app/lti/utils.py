from typing import Optional

from django.http.request import HttpRequest
from pylti1p3.exception import LtiException

from pylti1p3.contrib.django.message_launch import DjangoMessageLaunch
from pylti1p3.contrib.django.launch_data_storage.cache import DjangoCacheDataStorage
from pylti1p3.contrib.django.message_launch import DjangoMessageLaunch

from lti_tool.views import DjangoToolConfig
from lti_tool.models import (
    LtiLaunch,
)


def get_launch_from_request(
    request: HttpRequest, launch_id: Optional[str] = None
) -> LtiLaunch:
    """Returns the DjangoMessageLaunch associated with a request.

    Optionally, a launch_id may be specified to retrieve the launch from the cache.
    """
    tool_conf = DjangoToolConfig()
    launch_data_storage = DjangoCacheDataStorage()
    if launch_id is not None:
        message_launch = MateriaMessageLaunch.from_cache(
            launch_id, request, tool_conf, launch_data_storage=launch_data_storage
        )
    else:
        message_launch = MateriaMessageLaunch(
            request, tool_conf, launch_data_storage=launch_data_storage
        )
        message_launch.validate()
    return LtiLaunch(message_launch)

class MateriaMessageLaunch(DjangoMessageLaunch):

    def validate_state(self) -> "MateriaMessageLaunch":
        state_from_request = self._get_request_param("state")
        if not state_from_request:
            raise LtiException("Missing state param")

        id_token_hash = self._get_id_token_hash()
        if not self._session_service.check_state_is_valid(
            state_from_request, id_token_hash
        ):
            # state_from_cookie = self._cookie_service.get_cookie(state_from_request)
            # if state_from_request != state_from_cookie:
            #     # Error if state doesn't match.
            #     raise LtiException("State not found")
            pass

        return self

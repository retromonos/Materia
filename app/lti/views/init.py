import logging
import json

from django.conf import settings
from lti_tool.views import OIDCLoginInitView, DjangoToolConfig, get_launch_from_request
from pylti1p3.exception import OIDCException

from django.http import (
    HttpResponseBadRequest,
)

from django.shortcuts import render

from pylti1p3.contrib.django import DjangoCacheDataStorage, DjangoOIDCLogin
logger = logging.getLogger(__name__)


class MateriaOIDCLoginInitView(OIDCLoginInitView):

    def get(self, request, *args, **kwargs):
        """
        Overrides OIDCLoginInitView's `get` method to intercept and handle OIDCExceptions.
        The intended behavior is to handle situations where a LTI registration has been disabled.
        """
        print(request)
        registration_uuid = kwargs.get("registration_uuid")
        try:
            return self.get_oidc_response(request, registration_uuid, request.GET)
        except OIDCException:
            from lti.views.lti import error_page as lti_error_page

            return lti_error_page(request, "error_registration_disabled")

    def get_redirect_url(self, target_link_uri: str) -> str:
        """
        Overrides OIDCLoginInitView's `get_redirect_url` method, as we only have one whitelisted launch URI: /ltilaunch/
        LTI 1.3 requires all launch URIs to be whitelisted in platform's LTI key
        From the launch view (lti/views/launch.py), handle_resource_launch and handle_deep_linking_launch actually send
        the user where they want to go
        """
        redirect = f"{settings.URLS["BASE_URL"]}ltilaunch/"
        return redirect

    def get_oidc_response(self, request, registration_uuid, params):
        if params.get('lti_storage_target', None) == 'post_message_forwarding':
            tool_conf = DjangoToolConfig(registration_uuid)
            launch_data_storage = DjangoCacheDataStorage()
            oidc_login = DjangoOIDCLogin(
                request, tool_conf, launch_data_storage=launch_data_storage
            )

            target_link_uri = params.get("target_link_uri")
            if target_link_uri is None:
                return HttpResponseBadRequest("Missing target_link_uri parameter.")

            redirect_uri = oidc_login._prepare_redirect_url(target_link_uri)
            print(redirect_uri)

            return render(
                request, 
                "oidc_put.html", 
                {
                    "params": json.dumps(params),
                    "redirect_uri": redirect_uri
                }
            )
    
        return super().get_oidc_response(request, registration_uuid, params)

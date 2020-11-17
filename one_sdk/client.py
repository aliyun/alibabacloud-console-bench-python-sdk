import json

try:
    from urllib.parse import urlparse, urlencode
except ImportError:
    import urlparse
    from urllib import urlencode

from aliyunsdkcore.vendored.requests import codes
from aliyunsdkcore import compat
from aliyunsdkcore.acs_exception import error_code
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import RpcRequest
from aliyunsdkcore.auth.composer.rpc_signature_composer import (
    __refresh_sign_parameters,
    __compose_string_to_sign,
    __get_signature,
    __pop_standard_urlencode,
)
from aliyunsdkcore.http.http_response import HttpResponse
from aliyunsdkcore.auth.algorithm import sha_hmac1


def get_signed_url(params, ak, secret, accept_format, method, body_params, client_params):
    url_params = __refresh_sign_parameters(params, ak, accept_format, sha_hmac1)
    sign_params = dict(url_params)
    sign_params.update(body_params)

    sign_params.pop('IdToken', None)
    sign_params.pop('RiskCode', None)
    sign_params.pop('TraceId', None)
    sign_params.pop('AliUid', None)
    for k in client_params.keys():
        sign_params.pop(k, None)

    string_to_sign = __compose_string_to_sign(method, sign_params)
    signature = __get_signature(string_to_sign, secret, sha_hmac1)

    sign_params.pop('Product', None)
    sign_params.pop('Action', None)
    sign_params.pop('Version', None)
    sign_params.pop('Timestamp', None)
    sign_params.pop('SignatureMethod', None)
    sign_params.pop('SignatureType', None)
    sign_params.pop('SignatureVersion', None)
    sign_params.pop('SignatureNonce', None)
    sign_params.pop('AccessKeyId', None)
    sign_params.pop('Format', None)
    url_params['Params'] = json.dumps(sign_params)
    url_params['Signature'] = signature
    url = '?' + __pop_standard_urlencode(urlencode(url_params))
    return url, string_to_sign


class OneClient(AcsClient):
    def __init__(self,
                 ak=None,
                 secret=None,
                 region_id="cn-hangzhou",
                 auto_retry=True,
                 max_retry_time=None,
                 user_agent=None,
                 port=80,
                 connect_timeout=None,
                 timeout=None,
                 public_key_id=None,
                 private_key=None,
                 session_period=3600,
                 credential=None,
                 debug=False):
        super().__init__(ak, secret, region_id, auto_retry, max_retry_time, user_agent,
                         port, timeout, public_key_id, private_key, session_period,
                         credential, debug)
        self.query_params = {}
        self._endpoint = None
        self._read_timeout = timeout
        self._connect_timeout = connect_timeout

    def set_endpoint(self, endpoint):
        self._endpoint = endpoint

    def add_query_param(self, k, v):
        self.query_params[k] = v

    def do_action(self, acs_request):
        self.do_action_with_exception(acs_request)

    def do_action_with_exception(self, request: RpcRequest):
        request.set_accept_format('JSON')
        path = request.path_pattern if hasattr(request, 'path_pattern') else '/api/acs/openapi'

        if self._endpoint:
            endpoint = self._endpoint
        elif request.endpoint:
            endpoint = request.endpoint
        else:
            endpoint = self._resolve_endpoint(request)

        request.add_query_param('Product', request.get_product())
        request.add_query_param('RegionId', self.get_region_id())
        request.add_query_param('Action', request.get_action_name())
        request.add_query_param('Version', request.get_version())

        request._params.update(self.query_params)
        sign_params = dict(request._params)
        query, sign_str = get_signed_url(
            sign_params,
            self.get_access_key(),
            self.get_access_secret(),
            request.get_accept_format(),
            request.get_method(),
            request.get_body_params(),
            self.query_params
        )
        request.string_to_sign = sign_str

        endpoint += path
        response = HttpResponse(
            endpoint,
            query,
            request.get_method(),
            request.get_signed_header(self.get_region_id(), self.get_access_key(), self.get_access_secret()),
            request.get_protocol_type(),
            request.get_content(),
            self._port)

        if self._read_timeout:
            response._timeout = response.__read_timeout = self._read_timeout
        if self._connect_timeout:
            response.__connect_timeout = self._connect_timeout

        try:
            status, headers, body = response.get_response_object()
        except IOError as e:
            exception = ClientException(error_code.SDK_HTTP_ERROR, compat.ensure_string('%s' % e))
            return None, None, None, exception

        exception = self.get_server_exception(status, body)
        if exception:
            raise exception

        return body

    def get_server_exception(self, http_status, response_body):
        try:
            body_obj = json.loads(response_body.decode('utf-8'))
            request_id = body_obj.get('RequestId')
        except (ValueError, TypeError, AttributeError):
            raise RuntimeError('Failed to parse response as json format. Response:%s', response_body)

        if http_status < codes.OK or http_status >= codes.MULTIPLE_CHOICES:

            server_error_code, server_error_message = self._parse_error_info_from_response_body(
                response_body.decode('utf-8'))

            exception = ServerException(
                server_error_code,
                server_error_message,
                http_status=http_status,
                request_id=request_id)
            return exception

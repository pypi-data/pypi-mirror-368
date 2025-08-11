import requests
from oba import Obj
from smartdjango import Error, Code, OK


@Error.register
class QitianErrors:
    QITIAN_GET_USER_INFO_FAIL = Error("齐天簿获取用户信息失败", code=Code.InternalServerError)
    QITIAN_GET_USER_PHONE_FAIL = Error("齐天簿获取用户手机号失败", code=Code.InternalServerError)
    QITIAN_AUTH_FAIL = Error("齐天簿身份认证失败", code=Code.InternalServerError)
    QITIAN_REQ_FAIL = Error("齐天簿请求{target}失败", code=Code.InternalServerError)


class QitianManager:
    def __init__(self, app_id, app_secret, host, timeout=3):
        self.app_id = app_id
        self.app_secret = app_secret
        self.host = host
        self.timeout = timeout

    def set_timeout(self, timeout):
        self.timeout = timeout

    @staticmethod
    def _req_extractor(request: requests.Response, error: Error):
        if request.status_code != requests.codes.ok:
            raise error
        try:
            response = Obj(request.json())
        except Exception as err:
            raise error(details=err)

        if response.identifier != OK.identifier:
            raise error(append_message=response.user_message)

        return Obj.raw(response.body)

    def get_token(self, code):
        url = self.host + '/oauth/token'

        resp = requests.post(url, json=dict(
            code=code,
            app_secret=self.app_secret,
        ), timeout=self.timeout)

        return self._req_extractor(resp, QitianErrors.QITIAN_REQ_FAIL(target='身份认证'))

    def get_user_info(self, token):
        url = self.host + '/user/'

        resp = requests.get(url, headers=dict(
            token=token,
        ), timeout=self.timeout)

        return self._req_extractor(resp, QitianErrors.QITIAN_REQ_FAIL(target='用户信息'))

    def get_user_phone(self, token):
        url = self.host + '/user/phone/'

        resp = requests.get(url, headers=dict(
            token=token,
        ), timeout=self.timeout)

        return self._req_extractor(resp, QitianErrors.QITIAN_REQ_FAIL(target='用户手机号'))

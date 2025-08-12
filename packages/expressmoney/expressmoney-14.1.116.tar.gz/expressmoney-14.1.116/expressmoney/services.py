import json
import os
import time
from datetime import datetime, timedelta

import boto3
import jwt
import requests
import urllib3
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from requests import Timeout, ConnectionError
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
User = get_user_model()


class IamTokenService:
    URL = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'

    def __init__(self):
        authorized_key = json.loads(os.getenv('IAM'))
        self._service_account_id = authorized_key['service_account_id']
        self._key_id = authorized_key['id']
        self._private_key = authorized_key['private_key']
        self._iam_token = None
        self._expires_at = None

    def get_token(self):
        if self._expires_at and self._expires_at > datetime.now():
            return self._iam_token
        else:
            self._iam_token, self._expires_at = self._request()
        return self._iam_token

    def _request(self):
        now = int(time.time())
        payload = {
            'aud': self.URL,
            'iss': self._service_account_id,
            'iat': now,
            'exp': now + 360}
        encoded_token = jwt.encode(
            payload,
            self._private_key,
            algorithm='PS256',
            headers={'kid': self._key_id})
        response = requests.post(self.URL, json={'jwt': encoded_token}).json()
        return response['iamToken'], datetime.now() + timedelta(hours=1)


class RuSmsService:
    _url = 'https://omnichannel.mts.ru/http-api/v1/messages'

    def __init__(self, sender):
        self._login, self._password = os.getenv('MTS_SMS').split('||')
        self._sender = sender

    def send(self, phonenumber, message):
        response = requests.post(self._url,
                                 json=self._get_payload(phonenumber, self._sender, message),
                                 auth=HTTPBasicAuth(self._login, self._password),
                                 timeout=(30, 30)
                                 )
        if not status.is_success(response.status_code):
            raise ValidationError(response.text)
        result = self._get_result(response.json().get("messages")[0].get("internal_id"))
        self._handle_errors(result)

    def _get_result(self, internal_id):
        try:
            response_info = requests.post(url=f"{self._url}/info",
                                          json={"int_ids": [internal_id]},
                                          auth=HTTPBasicAuth(self._login, self._password), )
            return response_info.json().get('events_info')[0].get('events_info')[0]
        except (IndexError, TypeError, IOError):
            pass

    @staticmethod
    def _get_payload(phonenumber, sender, message):
        msisdn = f'{phonenumber.country_code}{phonenumber.national_number}'
        payload = {
            "messages": [
                {
                    "content": {
                        "short_text": message
                    },
                    "from": {
                        "sms_address": sender
                    },
                    "to": [
                        {
                            "msisdn": msisdn
                        }
                    ]
                }
            ]
        }
        return payload

    @staticmethod
    def _handle_errors(result):
        if not result:
            return
        internal_errors = result.get('internal_errors')
        if not internal_errors:
            return result
        elif 10802 in internal_errors:
            raise ValidationError('phonenumber_format_error')
        elif 10803 in internal_errors:
            raise ValidationError('unsupported_code_country')
        elif 10904 in internal_errors:
            raise ValidationError('phonenumber_blacklist')
        elif 10100 in internal_errors:
            raise ValidationError('incorrect_sender')
        else:
            raise ValidationError(internal_errors)


class YandexObjectService:
    _bucket = 'expressmoney'
    _filename = None

    def __init__(self):
        self._s3 = boto3.session.Session().client(service_name='s3', endpoint_url='https://storage.yandexcloud.net')

    def generate_key(self, filename):
        self._filename = filename
        prepared_form_fields = self._s3.generate_presigned_post(Bucket=self._bucket,
                                                                Key=f'files/{self._filename}',
                                                                Conditions=[["starts-with", "$key", "files"], ],
                                                                ExpiresIn=60 * 60)
        return json.dumps(prepared_form_fields)


class ScoringService:
    _url = 'https://api.expressmoney.com/ru_scoring/pdl_ru/scoring'

    def __init__(self):
        self._headers = {'Authorization': f'Token {os.getenv("SERVICE_TOKEN")}'}

    def request(self, data: dict) -> dict:
        attempts = 0
        response = self._request(attempts, data)
        order_id = data.get("order_id")
        if status.is_success(response.status_code):
            return response.json()
        elif response.status_code == status.HTTP_400_BAD_REQUEST and order_id:
            response = requests.get(f'{self._url}/{order_id}', headers=self._headers)
            if status.is_success(response.status_code):
                return response.json()
        raise ValidationError(response.text[:1024])

    def _request(self, attempts, data):
        try:
            response = requests.post(self._url, headers=self._headers, json=data, verify=False, timeout=(300, 300))
        except ConnectionError as e:
            attempts += 1
            if attempts <= 3:
                time.sleep(1)
                response = self._request(attempts, data)
            else:
                raise e
        return response


class RuPartnerService:
    SERVICE_URL = 'https://bbaic3serh6adpvivht0.containers.yandexcloud.net'

    def __init__(self):
        self._iam_token_service = IamTokenService()

    def create_lead(self, referral_id: int):
        url = f'{self.SERVICE_URL}/ru_partners/leads/lead'
        requests.post(url, headers=self._get_header(referral_id), data={'description': 1})

    def create_referral(self, referral_id, partner_code):
        url = f'{self.SERVICE_URL}/ru_partners/referrals/referral'
        requests.post(url, headers=self._get_header(referral_id), data={'partner_code': partner_code})

    def send_order_postback(self, user_id: int, order_id: int, utm_source: str, transaction_id: str, amount):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/order_client_post_back'
        requests.post(url,
                      headers=self._get_header(user_id),
                      data={
                          'order_id': order_id,
                          'utm_source': utm_source,
                          'transaction_id': transaction_id,
                          'amount': amount
                      })

    def send_approved_postback(self, user_id: int, order_id: int, utm_source: str, transaction_id: str, amount):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/approved_postback'
        requests.post(url,
                      headers=self._get_header(user_id),
                      data={
                          'order_id': order_id,
                          'utm_source': utm_source,
                          'transaction_id': transaction_id,
                          'amount': amount
                      })

    def send_loan_postback(self, user_id: int, loan_id: int, utm_source: str, transaction_id: str, amount):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/loan_client_post_back'
        requests.post(url, headers=self._get_header(user_id), data={
            'loan_id': loan_id,
            'utm_source': utm_source,
            'transaction_id': transaction_id,
            'amount': amount
        })

    def send_add_profile_postback(self, user_id: int, utm_source: str):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/send_add_profile_postback'
        requests.post(url, headers=self._get_header(user_id), data={
            'user_id': user_id,
            'utm_source': utm_source,
        })

    def send_order_postback_deeplink(self, user_id: int, order_id: int, phone_number: str, amount):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/order_user_post_back'
        requests.post(url,
                      headers=self._get_header(user_id),
                      data={
                          'order_id': order_id,
                          'phone_number': phone_number,
                          'amount': amount
                      })

    def send_loan_postback_deeplink(self, user_id: int, loan_id: int, phone_number: str, amount):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/loan_user_post_back'
        requests.post(url,
                      headers=self._get_header(user_id),
                      data={
                          'loan_id': loan_id,
                          'phone_number': phone_number,
                          'amount': amount
                      })

    def get_cpa_client(self, user_id: int):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/cpa_client/{user_id}'
        return requests.get(url, headers=self._get_header(user_id))

    def get_cpa_user(self, user_id: int, phone_number: str):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/cpa_user/{phone_number}'
        return requests.get(url, headers=self._get_header(user_id))

    def set_user_id(self, user_id: int, cpaclient: int):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/set_user_id'
        return requests.post(url, headers=self._get_header(user_id), json={'user_id': user_id, 'cpaclient': cpaclient})

    def is_full_deal(self, user_id: int):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/full_deal/is_full_deal'
        return requests.post(url, headers=self._get_header(user_id))

    def async_closed_confirm(self, user_id: int, loan_id: int):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/full_deal/async_closed_confirm'
        return requests.post(url, headers=self._get_header(user_id), json={'loan_id': loan_id})

    def payment_confirm(self, user_id: int, payload: dict):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/full_deal/payment_confirm'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(30, 30))

    def overdue_confirm(self, user_id: int, payload: dict):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/full_deal/overdue_confirm'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(10, 10))

    def prolonged_confirm(self, user_id: int, payload: dict):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/full_deal/prolonged_confirm'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(30, 30))

    def is_stop_full_deal(self, user_id: int):
        url = f'{self.SERVICE_URL}/ru_partners/cpa/full_deal/is_stop_full_deal'
        return requests.post(url, headers=self._get_header(user_id), timeout=(10, 10))

    def _get_header(self, user_id):
        refresh = RefreshToken.for_user(User.objects.get(pk=user_id))
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}',
            'Auth': f'Bearer {refresh.access_token}'
        }
        return headers


class AuthService:
    SERVICE_URL = 'https://bba6ogflnltlachiiqiu.containers.yandexcloud.net'

    def __init__(self):
        self.attempts = 0
        self._iam_token_service = IamTokenService()

    def list_sms(self, user_id: int):
        url = f'{self.SERVICE_URL}/auth/sms/sms'
        return requests.get(url, headers=self._get_header(user_id), timeout=(120, 120))

    def get_code(self, user_id: int):
        """Код для формирования url для автоматического входа без пароля"""
        try:
            headers = self._get_header(user_id)
            url = f'{self.SERVICE_URL}/auth/auto_login/code/{user_id}'
            response = requests.get(url, headers=headers, timeout=(120, 120))
            if status.is_success(response.status_code):
                return response.json().get('code')
            elif response.status_code == status.HTTP_404_NOT_FOUND:
                url = f'{self.SERVICE_URL}/auth/auto_login/code'
                response = requests.post(url, headers=headers, timeout=(120, 120))
                if not status.is_success(response.status_code):
                    raise ValidationError(response.text)
                return response.json().get('code')
            else:
                raise ValidationError(response.text)
        except Timeout as e:
            if self.attempts < 5:
                self.attempts += 1
                return self.get_code(user_id)
            else:
                raise e

    def create_user_ext(self, user_data: dict):
        user_id = int(os.getenv('SERVICE_USER_ID'))
        url = f'{self.SERVICE_URL}/auth/ext/ext'
        return requests.post(url, headers=self._get_header(user_id), json=user_data, timeout=(120, 120))

    def update_last_login(self, user_id):
        url = f'{self.SERVICE_URL}/auth/ext/user/{user_id}/update_last_login'
        return requests.post(url, headers=self._get_header(user_id))

    def get_user_id(self, phonenumber: str):
        url = f'{self.SERVICE_URL}/auth/ext/user/get_user_id'
        response = requests.post(url, data={'phonenumber': phonenumber}, headers=self._get_header_allowany())
        return response.json().get('user_id')

    def list_provider(self, user_id):
        url = f'{self.SERVICE_URL}/auth/providers/provider'
        return requests.get(url, headers=self._get_header(user_id))

    def get_provider_data(self, provider_token, provider):
        url = f'{self.SERVICE_URL}/auth/providers/provider_data'
        return requests.post(url, data={'provider_token': provider_token,
                                        'provider': provider}, headers=self._get_header_allowany())

    def get_provider_data_id(self, provider_id):
        url = f'{self.SERVICE_URL}/auth/providers/provider_data/{provider_id}'
        return requests.get(url, headers=self._get_header_allowany())

    def _get_header_allowany(self) -> dict:
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}'
        }
        return headers

    def _get_header(self, user_id: int) -> dict:
        refresh = RefreshToken.for_user(User.objects.get(pk=user_id))
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}',
            'Auth': f'Bearer {refresh.access_token}'
        }
        return headers


class RuProfilesService:
    SERVICE_URL = 'https://bbaqp3g26tvqqijq9rdn.containers.yandexcloud.net'

    def __init__(self, api_version=''):
        self._iam_token_service = IamTokenService()
        self._api_version = api_version

    def create_profile(self, user_id: int, profile_data: dict):
        url = f'{self.SERVICE_URL}/ru_profiles/profiles/profile'
        return requests.post(url, headers=self._get_header(user_id), json=profile_data, timeout=(120, 120))

    def request_inn(self, payload):
        user_id = int(os.getenv('SERVICE_USER_ID'))
        url = f'{self.SERVICE_URL}/ru_profiles/profiles/inn/request_inn'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(120, 120))

    def request_prohibition(self, payload):
        user_id = int(os.getenv('SERVICE_USER_ID'))
        url = f'{self.SERVICE_URL}/ru_profiles/profiles/prohibition/request_prohibition'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(120, 120))

    def set_inn(self, user_id, payload):
        url = f'{self.SERVICE_URL}/ru_profiles/profiles/profile/{user_id}/set_inn'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(120, 120))

    def _get_header(self, user_id: int) -> dict:
        refresh = RefreshToken.for_user(User.objects.get(pk=user_id))
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}',
            'Auth': f'Bearer {refresh.access_token}',
            'Accept': f'application/json; version={self._api_version}'
        }
        return headers


class RuLoansService:
    SERVICE_URL = 'https://bbavf0h1b2vaed78vvsf.containers.yandexcloud.net'

    def __init__(self):
        self._iam_token_service = IamTokenService()

    def create_order(self, user_id: int, order_data: dict):
        url = f'{self.SERVICE_URL}/ru_loans/orders/order'
        return requests.post(url, headers=self._get_header(user_id), json=order_data, timeout=(120, 120))

    def create_loan(self, user_id: int, loan_data: dict):
        url = f'{self.SERVICE_URL}/ru_loans/loans/loan'
        return requests.post(url, headers=self._get_header(user_id), json=loan_data, timeout=(120, 120))

    def body_issue(self, user_id, loan_id, bank_card_id):
        payload = {
            'loan': loan_id,
            'bank_card_id': bank_card_id
        }
        url = f'{self.SERVICE_URL}/ru_loans/operations/body_issue'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(120, 120))

    def create_provider_bonus(self, user_id):
        url = f'{self.SERVICE_URL}/ru_loans/bonuses/bonus/create_provider'
        return requests.post(url, headers=self._get_header(user_id), timeout=(120, 120))

    def send_sign(self, user_id: int, order_id: int):
        url = f'{self.SERVICE_URL}/ru_loans/orders/order/{order_id}/send_sign'
        return requests.post(url, headers=self._get_header(user_id), timeout=(120, 120))

    def set_duty(self, loan_id, payload):
        user_id = int(os.getenv('SERVICE_USER_ID'))
        url = f'{self.SERVICE_URL}/ru_loans/loans/loan/{loan_id}/set_duty'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(120, 120))

    def set_duty_paid(self, loan_id, payload):
        user_id = int(os.getenv('SERVICE_USER_ID'))
        url = f'{self.SERVICE_URL}/ru_loans/loans/loan/{loan_id}/set_duty_paid'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(120, 120))

    def _get_header(self, user_id: int) -> dict:
        refresh = RefreshToken.for_user(User.objects.get(pk=user_id))
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}',
            'Auth': f'Bearer {refresh.access_token}',
        }
        return headers


class RuCollectionService:
    SERVICE_URL = 'https://bbaf54ojmpa33hsuljc8.containers.yandexcloud.net'

    def __init__(self):
        self._iam_token_service = IamTokenService()

    def create_pay_duty(self, payload):
        user_id = int(os.getenv('SERVICE_USER_ID'))
        url = f'{self.SERVICE_URL}/ru_collection/operations/pay_duty'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(120, 120))

    def amount_by_pay_id(self, payload):
        user_id = int(os.getenv('SERVICE_USER_ID'))
        url = f'{self.SERVICE_URL}/ru_collection/operations/pay_duty/amount_by_pay_id'
        return requests.post(url, headers=self._get_header(user_id), json=payload, timeout=(120, 120))

    def find_pay_duty(self, payload):
        user_id = int(os.getenv('SERVICE_USER_ID'))
        url = f'{self.SERVICE_URL}/ru_collection/operations/pay_duty'
        return requests.get(url, headers=self._get_header(user_id), params=payload, timeout=(120, 120))

    def _get_header(self, user_id: int) -> dict:
        refresh = RefreshToken.for_user(User.objects.get(pk=user_id))
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}',
            'Auth': f'Bearer {refresh.access_token}',
        }
        return headers


class FraudProcessService:
    SERVICE_URL = 'https://bbaqp3g26tvqqijq9rdn.containers.yandexcloud.net'

    def __init__(self, api_version=''):
        self._iam_token_service = IamTokenService()
        self._api_version = api_version

    def create(self, user_id, comment):
        url = f'{self.SERVICE_URL}/ru_profiles/profiles/fraud_process'
        response = requests.post(url, headers=self._get_header(user_id), json={'comment': comment})
        return response

    def _get_header(self, user_id: int) -> dict:
        refresh = RefreshToken.for_user(User.objects.get(pk=user_id))
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}',
            'Auth': f'Bearer {refresh.access_token}',
            'Accept': f'application/json; version={self._api_version}'
        }
        return headers


class HolderNameProcessService:
    SERVICE_URL = 'https://bbaqp3g26tvqqijq9rdn.containers.yandexcloud.net'

    def __init__(self, api_version=''):
        self._iam_token_service = IamTokenService()
        self._api_version = api_version

    def create(self, user_id, bank_card_id):
        url = f'{self.SERVICE_URL}/ru_profiles/profiles/holder_name_process'
        response = requests.post(url, headers=self._get_header(user_id), json={'bank_card_id': bank_card_id})
        return response

    def _get_header(self, user_id: int) -> dict:
        refresh = RefreshToken.for_user(User.objects.get(pk=user_id))
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}',
            'Auth': f'Bearer {refresh.access_token}',
            'Accept': f'application/json; version={self._api_version}'
        }
        return headers


class BlackListService:
    SERVICE_URL = 'https://bba6ogflnltlachiiqiu.containers.yandexcloud.net'

    def __init__(self):
        self._iam_token_service = IamTokenService()

    def create(self, user_id, cause, comment):
        url = f'{self.SERVICE_URL}/auth/black_list/black_list'
        response = requests.post(url, headers=self._get_header(user_id), json={'cause': cause, 'comment': comment})
        return status.is_success(response.status_code)

    def retrieve(self, user_id):
        url = f'{self.SERVICE_URL}/auth/black_list/black_list/{user_id}'
        response = requests.get(url, headers=self._get_header(user_id))
        return response.json().get('cause'), response.json().get('comment')

    def delete(self, user_id):
        url = f'{self.SERVICE_URL}/auth/black_list/black_list/{user_id}'
        response = requests.delete(url, headers=self._get_header(user_id))
        return status.is_success(response.status_code)

    def find(self, user_id):
        url = f'{self.SERVICE_URL}/auth/black_list/black_list/find'
        response = requests.post(url, headers=self._get_header(user_id))
        return response.json().get('is_black_list'), response.json().get('cause')

    def _get_header(self, user_id: int) -> dict:
        refresh = RefreshToken.for_user(User.objects.get(pk=user_id))
        headers = {
            'Authorization': f'Bearer {self._iam_token_service.get_token()}',
            'Auth': f'Bearer {refresh.access_token}',
            'Accept': f'application/json'
        }
        return headers

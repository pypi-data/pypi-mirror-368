from .utils import Bearer, Cookie, Generator, Useragent
from .client import Client
from .guest import Guest

import requests
import time
import json
import re

def unescape_string(escaped_str):
    replacements = {
        r'\b': '\b',
        r'\f': '\f',
        r'\n': '\n',
        r'\r': '\r',
        r'\t': '\t',
        r'\"': '"',
        r'\\': '\\'
    }
    results = escaped_str
    for escaped, unescaped in replacements.items():
        results = results.replace(escaped, unescaped)
    return results

def decode_multiple_unescapes(text, count=4):
    results = text
    for i in range(count):
        results = unescape_string(str(results))
    return results

class Checker:
    
    @staticmethod
    def headers():
        return {
            'x-ig-app-locale': 'in_ID',
            'x-ig-device-locale': 'in_ID',
            'x-ig-mapped-locale': 'in_ID',
            'x-pigeon-session-id': Generator.pigeon_session_id(),
            'x-pigeon-rawclienttime': Generator.pigeon_rawclienttime(),
            'x-ig-bandwidth-speed-kbps': Generator.speed_kbps(),
            'x-ig-bandwidth-totalbytes-b': str(Generator.total_bytes_b()),
            'x-ig-bandwidth-totaltime-ms': str(Generator.total_time_ms()),
            'x-bloks-version-id': '16e9197b928710eafdf1e803935ed8c450a1a2e3eb696bff1184df088b900bcf',
            'x-ig-www-claim': '0',
            'x-bloks-prism-button-version': 'CONTROL',
            'x-bloks-prism-colors-enabled': 'false',
            'x-bloks-prism-ax-base-colors-enabled': 'false',
            'x-bloks-prism-font-enabled': 'false',
            'x-bloks-is-layout-rtl': 'false',
            'x-ig-device-id': Generator.device_id(),
            'x-ig-family-device-id': Generator.family_device_id(),
            'x-ig-android-id': Generator.android_id(),
            'x-ig-timezone-offset': Generator.timezone_offset(),
            'x-ig-nav-chain': 'com.bloks.www.caa.login.login_homepage:com.bloks.www.caa.login.login_homepage:1:button:1737175594.533::',
            'x-fb-connection-type': 'WIFI',
            'x-ig-connection-type': 'WIFI',
            'x-ig-capabilities': '3brTv10=',
            'x-ig-app-id': '567067343352427',
            'priority': 'u=3',
            'user-agent': Useragent.instagram(),
            'accept-language': 'in-ID, en-US',
            'x-mid': Generator.machine_id(),
            'ig-intended-user-id': '0',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'x-fb-http-engine': 'Liger',
            'x-fb-client-ip': 'True',
            'x-fb-server-cluster': 'True'
        }
    
    @staticmethod
    def username(username: str):
        account = Guest.username_info(username)
        return True if account and account.username else False
    
    @staticmethod
    def cookies(cookies: str | dict):
        if isinstance(cookies, dict):
            cookies = Cookie.to_str(cookies)
        session = Client(cookies)
        account = session.account_info()
        return True if account and account.username else False
    
    @staticmethod
    def password(username: str, password: str, **kwargs):
        session = requests.Session()
        headers = Login.headers()
        device_id = headers['x-ig-device-id']
        machine_id = headers['x-mid']
        android_id = headers['x-ig-android-id']
        family_device_id = headers['x-ig-family-device-id']
        user_agent = kwargs.pop('user_agent', None)
        if user_agent:
            user_agent_data = Useragent.parser(user_agent)
            headers['user-agent'] = user_agent
            headers['x-ig-app-locale'] = user_agent_data['android_language'].replace('-','_')
            headers['x-ig-device-locale'] = user_agent_data['android_language'].replace('-','_')
            headers['x-ig-mapped-locale'] = user_agent_data['android_language'].replace('-','_')
            headers['accept-language'] = user_agent_data['android_language'].replace('_','-') + ', en-US'
        data = {
           'params': json.dumps({
               'client_input_params': {
                   'sim_phones': [],
                   'secure_family_device_id': '',
                   'has_granted_read_contacts_permissions': 0,
                   'auth_secure_device_id': '',
                   'has_whatsapp_installed': 0,
                   'password': f'#PWD_INSTAGRAM:0:{int(time.time())}:{password}',
                   'sso_token_map_json_string': '',
                   'event_flow': 'login_manual',
                   'password_contains_non_ascii': 'false',
                   'client_known_key_hash': '',
                   'encrypted_msisdn': '',
                   'has_granted_read_phone_permissions': 0,
                   'app_manager_id': '',
                   'should_show_nested_nta_from_aymh': 0,
                   'device_id': android_id,
                   'login_attempt_count': 1,
                   'machine_id': machine_id,
                   'flash_call_permission_status': {
                       'READ_PHONE_STATE': 'DENIED',
                       'READ_CALL_LOG': 'DENIED', 
                       'ANSWER_PHONE_CALLS': 'DENIED'
                   },
                   'accounts_list': [],
                   'family_device_id': family_device_id,
                   'fb_ig_device_id': [],
                   'device_emails': [],
                   'try_num': 2,
                   'lois_settings': {
                       'lois_token': ''
                   },
                   'event_step': 'home_page',
                   'headers_infra_flow_id': '',
                   'openid_tokens': {},
                   'contact_point': username
               },
               'server_params': {
                   'should_trigger_override_login_2fa_action': 0,
                   'is_from_logged_out': 0, 
                   'should_trigger_override_login_success_action': 0,
                   'login_credential_type': 'none',
                   'server_login_source': 'login',
                   'waterfall_id': Generator.uuid(),
                   'login_source': 'Login',
                   'is_platform_login': 0,
                   'INTERNAL__latency_qpl_marker_id': 36707139,
                   'offline_experiment_group': 'caa_iteration_v3_perf_ig_4',
                   'is_from_landing_page': 0,
                   'password_text_input_id': 'phug4p:100',
                   'is_from_empty_password': 0,
                   'is_from_msplit_fallback': 0,
                   'ar_event_source': 'login_home_page',
                   'qe_device_id': device_id,
                   'username_text_input_id': 'phug4p:99',
                   'layered_homepage_experiment_group': None,
                   'device_id': android_id,
                   'INTERNAL__latency_qpl_instance_id': 1.54162845700187E14,
                   'reg_flow_source': 'login_home_native_integration_point',
                   'is_caa_perf_enabled': 1,
                   'credential_type': 'password',
                   'is_from_password_entry_page': 0,
                   'caller': 'gslr',
                   'family_device_id': family_device_id,
                   'is_from_assistive_id': 0,
                   'access_flow_version': 'F2_FLOW',
                   'is_from_logged_in_switcher': 0
               }
           }, separators=(',',':')),
           'bk_client_context': '{"bloks_version":"16e9197b928710eafdf1e803935ed8c450a1a2e3eb696bff1184df088b900bcf","styles_id":"instagram"}',
           'bloks_versioning_id': '16e9197b928710eafdf1e803935ed8c450a1a2e3eb696bff1184df088b900bcf'
        }
        url = 'https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.bloks.caa.login.async.send_login_request/'
        response = requests.post(
            url,
            headers=headers,
            data=data,
            **kwargs
        )
        response_text = decode_multiple_unescapes(response.text)
        return True if 'Bearer IGT:2' in response_text else False
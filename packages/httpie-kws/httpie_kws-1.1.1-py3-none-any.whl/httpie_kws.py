"""
KWS auth plugin for HTTPie.

"""
import os
import sys

from httpie.status import ExitStatus
from httpie.plugins import AuthPlugin
import hashlib
from datetime import datetime, timezone
from urllib3.util import parse_url
from pathlib import Path


__version__ = '1.1.0'
__author__ = 'Luo Jiejun'
__licence__ = 'Apache'


class KwsAppAuth:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    @staticmethod
    def hash_data(data: bytes):
        md5sign = hashlib.md5()
        md5sign.update(data)
        return md5sign.hexdigest()

    @staticmethod
    def hash_signature(sig: str):
        return KwsAppAuth.hash_data(sig.encode('utf-8'))

    def __call__(self, r):
        uri = parse_url(r.url)
        host = uri.host

        body = r.body
        if body is None:
            content_md5 = 'd41d8cd98f00b204e9800998ecf8427e'
        else:
            content_md5 = self.hash_data(body)

        now = datetime.now(tz=timezone.utc).isoformat()
        date = now
        signature = host + date + content_md5 + self.app_secret
        credential = self.app_id + '/' + now

        r.headers.update({'Authorization': 'KND-MD5 '
                                           'Credential=%s '
                                           'SignedHeaders=host;x-knd-date;x-knd-content-md5 '
                                           'Signature=%s' % (credential, self.hash_signature(signature)),
                          'X-Knd-Date': date,
                          'X-Knd-Content-MD5': content_md5})

        return r


class KwsAuthPlugin(AuthPlugin):
    name = 'KWS auth'
    auth_type = 'kws'
    description = 'KWS app authorization'
    auth_require = False
    prompt_password = True

    @staticmethod
    def parse_auth_file(path: Path):
        with open(path) as f:
            for line in f:
                name, val = line.strip().split(":")
                if name == "appid":
                    app_id = val
                elif name == "appsecret":
                    app_secret = val
        return app_id, app_secret

    def get_auth(self, username=None, password=None):
        env_key = 'KWS_APP_ID'
        env_secret = 'KWS_APP_SECRET'
        auth_file_path = Path.home() / '.kws-auth'

        app_id = os.environ.get(env_key) if username is None else username
        app_secret = os.environ.get(env_secret) if password is None else password

        if app_id is None or app_secret is None:
            try:
                app_id_, app_secret_ = self.parse_auth_file(auth_file_path)
                app_id, app_secret = app_id_, app_secret_
            except:
                missing = []
                if not app_id:
                    missing.append(env_key)
                if not app_secret:
                    missing.append(env_secret)
                if not auth_file_path.exists():
                    missing.append(str(auth_file_path))
                sys.stderr.write(
                    f'httpie-kws-auth error: missing {" and ".join(missing)}\n'
                )
                sys.exit(ExitStatus.PLUGIN_ERROR)

        return KwsAppAuth(app_id, app_secret)

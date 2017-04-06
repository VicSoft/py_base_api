# -*- coding: utf-8 -*-
import uuid
import json
import smtplib
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import RedirectView
from django.contrib.sessions.backends.db import SessionStore
from ...settings import API_PROJECT, os
from ..models import *
from ..platform_config import config, encryptSHA512
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import timedelta


class AbstractRest(RedirectView):
    http_status_code = {
        'success': 200,
        'not_found': 404,
        'server_error': 500,
        'method_not_allowed': 405,
        'unauthorized': 401,
        'request_not_authenticated': 403
    }
    hours_for_token_expiration = 2
    params = {}
    session_store = None
    mail_expires_days = 7
    base_project_url = 'http://oze.digital/'

    def __init__(self):
        config()

    def get(self, request, *args, **kwargs):
        return self.method_not_allowed()

    def post(self, request, *args, **kwargs):
        """TO GET BODY CONTENT USE: request.body AND YOU'LL RECEIVE AN DICTIONARY FROM BODY CONTENT"""
        return self.method_not_allowed()

    def put(self, request, *args, **kwargs):
        """TO GET BODY CONTENT USE: request.body AND YOU'LL RECEIVE AN DICTIONARY FROM BODY CONTENT"""
        return self.method_not_allowed()

    def delete(self, request, *args, **kwargs):
        return self.method_not_allowed()

    def patch(self, request, *args, **kwargs):
        return self.method_not_allowed()

    def method_not_allowed(self, msg='Method Not Allowed'):
        result_data = {
            'message': msg
        }
        result = self.set_response(
            success_state=False,
            status_code=self.http_status_code['method_not_allowed'],
            data=result_data
        )

        return result

    def parent_parsing(self, array=[], position_of_array=0, object={}):
        if len(object) > 0:
            self.params = object
        elif len(array) == 1:
            self.params = {
                'param': array[position_of_array]
            }
        else:
            self.params = array

    def load_session_by_token(self, token):
        response_data = defaultdict(dict)
        response_data['success'] = False
        response_data['data']['token'] = token

        with db_session:
            platformAccessByToken = PlatformAccess.select(lambda pa: (pa.token == token) and pa.isOnline).first()
            response_data['data']['expires_at'] = datetime.now()

            if platformAccessByToken:
                user_session = platformAccessByToken.user
                platformAccessBySession = PlatformAccess.select(lambda pa: pa.isOnline and (pa.token == token) and (pa.user == user_session)).first()

                if platformAccessBySession:
                    self.session_store = SessionStore(session_key=platformAccessBySession.sessionId)

                    if self.session_store:
                        response_data['data']['user'] = self.session_store.get('user')
                        response_data['data']['accessed_by'] = 'Web' if platformAccessBySession.isWeb else 'Mobile'
                        response_data['data']['expires_at'] = platformAccessBySession.tokenExpiresAt
                        response_data['success'] = True
                    else:
                        platformAccessBySession.isOnline = False
                        platformAccessBySession.update = datetime.now()
                        platformAccessBySession.flush()

            return response_data

    def prepare_email(self, mail_to, name_mail_to, subject, content_body, mail_from="OZé Digital <atendimento@oze.digital>"):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_from
        is_formatted = False

        if ("<" in mail_to) and (">" in mail_to):
            is_formatted = True
        else:
            mail_to = mail_to.replace(">", "").replace("<", "")

        mail_to = name_mail_to + (("<" + mail_to + ">") if not is_formatted else mail_to)
        msg['To'] = mail_to
        part_html = MIMEText(content_body, 'html')

        msg.attach(part_html)

        s = smtplib.SMTP('localhost')
        s.sendmail(mail_from, mail_to, msg.as_string())

        return s

    def isExpiredTokenByDateTime(self, platformAccess, expiresDate):
        if datetime.now() >= expiresDate:
            with db_session:
                platformAccess.updated = datetime.now()
                platformAccess.tokenExpiresAt = datetime.now() + timedelta(hours=self.hours_for_token_expiration)
                platformAccess.isOnline = False
                platformAccess.flush()
            return True
        return False

    def authenticateToken(self, token):
        with db_session:
            platformAccess = PlatformAccess.select(lambda pa: (pa.token in token) and pa.isOnline).first()

            if platformAccess and platformAccess.user.isActive:
                return not self.isExpiredTokenByDateTime(platformAccess, platformAccess.tokenExpiresAt)
            else:
                if platformAccess and not platformAccess.user.isActive:
                    platformAccess.tokenExpiresAt = datetime.now()
                    platformAccess.updated = datetime.now()
                    platformAccess.isOnline = False
                    flush()
                return False

    def generateTokenAccess(self):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, format(datetime.now())))

    @staticmethod
    def set_response(status_code=http_status_code['success'], data={}, success_state=True):
        HttpResponse.status_code = status_code

        return JsonResponse({
            'success': success_state,
            'data': data
        })

    @staticmethod
    def convert_str_to_datetime(str_datetime):
        return datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S')

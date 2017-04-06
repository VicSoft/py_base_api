# -*- coding: utf-8 -*-
from ...views.abstract_rest import *


class OzeAdmin(AbstractRest):

    def __init__(self):
        super(OzeAdmin, self).__init__()

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if ('username' not in data) and ('password' not in data):
            return self.method_not_allowed(msg='Username and Password keys on body payload must be specified')
        if ('is_web' not in data) or (not isinstance(data.get('is_web'), bool)):
            return self.method_not_allowed(msg="Format for 'is_web' key not allowed, it must be a boolean")

        username = data['username']
        password = encryptSHA512(data['password'])
        is_web = data.get('is_web')
        response_data = defaultdict(dict)
        response_status_code = self.http_status_code['success']
        success = False
        with db_session:
            user = User.select(lambda u: u.email == username).first()
            authenticateUser = lambda: (
                UserPassword.select(
                    lambda up: (up.user == user) and (up.password == password) and up.isCurrent
                ).first()
            )

            userPassword = authenticateUser()

            if userPassword:
                success = True
                platformAccess = PlatformAccess.select(
                    lambda pa: (pa.user == userPassword.user) and pa.isOnline
                ).first()
                tokenUser = None
                isAuthenticated = False

                if platformAccess:
                    isAuthenticated = self.authenticateToken(token=platformAccess.token)

                    if not isAuthenticated:
                        tokenUser = self.generateTokenAccess()

                if tokenUser is None:
                    tokenUser = self.generateTokenAccess()

                if not isAuthenticated:
                    expiry_at = (datetime.now() + timedelta(hours=self.hours_for_token_expiration))
                    self.session_store = SessionStore()
                    self.session_store['user'] = user.json_data()
                    # self.session_store.set_expiry(self.hours_for_token_expiration * 60)
                    self.session_store.create()

                    platformAccess = PlatformAccess(
                                        user=userPassword.user,
                                        isOnline=True,
                                        isWeb=is_web,
                                        token=tokenUser,
                                        sessionId=self.session_store.session_key,
                                        tokenExpiresAt=expiry_at
                                    ).flush()

                response_data = platformAccess.json_identity()
            else:
                response_status_code = self.http_status_code['not_found']
                response_data['message'] = "User not found"
            return self.set_response(data=response_data, success_state=success, status_code=response_status_code)

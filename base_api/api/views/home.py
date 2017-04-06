# -*- coding: utf-8 -*-
from abstract_rest import AbstractRest


class Home(AbstractRest):

    def get(self, request, *args, **kwargs):
        return self.set_response(data={
            'error': 'You need to authenticate on each request.',
            'message': 'Hello! This route is only for presenting something.'
        }, status_code=self.http_status_code['unauthorized'], success_state=False)

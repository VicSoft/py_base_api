# -*- coding: utf-8 -*-
from ....views.abstract_rest import *


class TestMail(AbstractRest):

    def __init__(self):
        super(TestMail, self).__init__()

    def get(self, request, *args, **kwargs):
        html = """\
        <html>
            <head>
                <meta charset="utf-8"/>
                <meta http-equiv="Content-type" content="text/html; charset=utf-8">
            </head>
            <body>
                <h4>Olá Victor tudo bem?</h4>
                <p>
                </p>
                <p>
                    Para alterar sua senha basta clicar <a href=""" + '"' + self.base_project_url + """atualizar-senha/234234234" target="_blank">aqui</a>.
                </p>
                <p>
                    <b>PS: </b>O link estará ativo por """ + format(self.mail_expires_days) + """ dias contados a partir da data deste e-mail.
                </p>
            </body>
        </html>
        """

        try:
            sender = self.prepare_email(mail_to="victor@gmail.com",
                                        name_mail_to="Victor Barbosa",
                                        subject="Recuperar senha de acesso",
                                        content_body=html)
            sender.quit()

            return self.set_response(status_code=200,
                                         data={'message': 'Your e-mail was successfully set. Thanks!'},
                                         success_state=True)
        except smtplib.SMTPResponseException as e:
            return self.set_response(status_code=self.http_status_code['server_error'],
                                         data={
                                             'error': e.smtp_error,
                                             'smtp_code': e.smtp_code
                                         },
                                         success_state=False)
        except smtplib.SMTPServerDisconnected as e:
            return self.set_response(status_code=self.http_status_code['server_error'],
                                         data={
                                             'error': e.smtp_error,
                                             'smtp_code': e.smtp_code
                                         },
                                         success_state=False)
        except smtplib.SMTPServerDisconnected as e:
            return self.set_response(status_code=self.http_status_code['server_error'],
                                         data={
                                             'error': e.smtp_error,
                                             'smtp_code': e.smtp_code
                                         },
                                         success_state=False)
        except Exception as e:
            return self.set_response(status_code=self.http_status_code['server_error'],
                                         data={
                                             'error': e.message
                                         },
                                         success_state=False)

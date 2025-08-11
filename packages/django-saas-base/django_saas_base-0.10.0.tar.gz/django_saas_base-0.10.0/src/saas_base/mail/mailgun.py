import typing as t
import requests
from .base import BaseMailProvider


class MailgunProvider(BaseMailProvider):
    name = 'mailgun'

    def get_api_url(self) -> str:
        domain = self.options['domain']
        return f'https://api.mailgun.net/v3/{domain}/messages'

    def get_api_auth(self):
        return 'api', self.options['api_key']

    def send_mail(
        self,
        subject: str,
        recipients: t.List[str],
        text_message: str,
        html_message: t.Optional[str] = None,
        from_email: t.Optional[str] = None,
        headers: t.Optional[t.Dict[str, str]] = None,
        reply_to: t.Optional[str] = None,
        fail_silently: bool = False,
    ):
        if from_email is None:
            from_email = self.default_from_email
        url = self.get_api_url()
        auth = self.get_api_auth()
        data = {
            'from': from_email,
            'to': recipients,
            'subject': subject,
            'text': text_message,
            'html': html_message,
        }
        if reply_to:
            data['h:Reply-To'] = reply_to
        for k in headers:
            data[f'h:{k}'] = headers[k]
        return requests.post(url, auth=auth, data=data)

import typing as t
from django.core.mail import EmailMultiAlternatives, get_connection
from .base import BaseMailProvider


class DjangoMailProvider(BaseMailProvider):
    name = 'django'

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
        connection = get_connection(fail_silently=fail_silently)
        mail = EmailMultiAlternatives(
            subject,
            body=text_message,
            from_email=from_email,
            to=recipients,
            connection=connection,
            headers=headers,
            reply_to=reply_to,
        )
        if html_message:
            mail.attach_alternative(html_message, 'text/html')
        return mail.send()

import typing as t
from .base import BaseMailProvider, render_mail_messages
from .django import DjangoMailProvider
from ..signals import mail_queued
from ..settings import saas_settings


def get_mail_provider(name: str = 'default') -> t.Optional[BaseMailProvider]:
    if name in saas_settings.MAIL_PROVIDERS:
        return saas_settings.MAIL_PROVIDERS[name]


class SendEmailMixin:
    email_provider: str = 'default'
    email_subject: str
    email_template_id: str

    def get_email_subject(self):
        return self.email_subject

    def send_email(self, recipients, **context):
        context.setdefault('site', saas_settings.SITE)
        if saas_settings.MAIL_IMMEDIATE_SEND:
            provider = get_mail_provider(self.email_provider)
            provider.send_context_mail(
                subject=self.get_email_subject(),
                template_id=self.email_template_id,
                recipients=recipients,
                context=context,
            )
        else:
            mail_queued.send(
                sender=self.__class__,
                subject=self.get_email_subject(),
                template_id=self.email_template_id,
                recipients=recipients,
                context=context,
            )


__all__ = [
    'get_mail_provider',
    'render_mail_messages',
    'BaseMailProvider',
    'DjangoMailProvider',
    'SendEmailMixin',
]

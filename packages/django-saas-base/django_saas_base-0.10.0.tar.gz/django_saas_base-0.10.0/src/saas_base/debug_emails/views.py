from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from ..models import Tenant, Member
from ..mail import render_mail_messages
from ..settings import saas_settings


def view_signup_code(request, suffix: str):
    context = {
        'code': 'ABCD',
        'site': saas_settings.SITE,
    }
    return _render_response('signup_code', context, suffix)


def view_reset_password(request, suffix: str):
    context = {
        'code': 'ABCD',
        'site': saas_settings.SITE,
        'user': User(username='alice', first_name='Alice'),
    }
    return _render_response('reset_password', context, suffix)


def view_invite_member(request, suffix: str):
    tenant = Tenant(slug='acme')
    context = dict(
        site=saas_settings.SITE,
        inviter=User(username='alice', first_name='Alice'),
        member=Member(email='bob@example.com', tenant=tenant),
        tenant=tenant,
        invite_link='#',
    )
    return _render_response('invite_member', context, suffix)


def _render_response(template, context, suffix: str):
    text_message, html_message = render_mail_messages(template, context)
    if suffix == 'txt':
        return HttpResponse(text_message, content_type='text/plain')
    elif suffix == 'html':
        return HttpResponse(html_message, content_type='text/html')
    else:
        raise Http404

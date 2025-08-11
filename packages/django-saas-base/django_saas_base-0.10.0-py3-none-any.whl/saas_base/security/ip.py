from rest_framework.settings import api_settings
from ..settings import saas_settings

__all__ = ['get_client_ip']


CLIENT_IP_HEADERS = (
    'Forwarded-For',  # Standard header defined by RFC 7239.
    'X-Forwarded-For',  # Common header for proxies, load balancers, like AWS ELB. Default to the left-most IP.
    'CF-Connecting-IP',  # Used by CloudFlare.
    'True-Client-IP',  # Header for CloudFlare Enterprise.
    'X-Real-IP',  # Header used by some providers like Amazon EC2, Heroku.
    'Client-IP',  # Header used by some providers like Amazon EC2, Heroku.
    'X-Client-IP',  # Used by Microsoft Azure.
    'Forwarded',  # Standard header defined by RFC 7239.
    'X-Forwarded',  # Used by Squid and similar software.
    'X-Cluster-Client-IP',  # Used by Rackspace Cloud Load Balancers.
    'Fastly-Client-IP',  # Used by Fastly, Firebase.
)


def get_client_ip(request, ip_headers=None):
    remote_addr = request.META.get('REMOTE_ADDR')

    if ip_headers is None:
        if saas_settings.CLIENT_IP_HEADERS:
            ip_headers = saas_settings.CLIENT_IP_HEADERS
        else:
            ip_headers = CLIENT_IP_HEADERS

    for key in ip_headers:
        ip = request.headers.get(key)
        if ip:
            if ',' in ip:
                return _parse_proxied_ip(ip, remote_addr)
            return ip

    return remote_addr


def _parse_proxied_ip(xff: str, remote_addr: str):
    num_proxies = api_settings.NUM_PROXIES

    if num_proxies is not None:
        if num_proxies == 0 or xff is None:
            return remote_addr

        addresses = xff.split(',')
        client_addr = addresses[-min(num_proxies, len(addresses))]
        return client_addr.strip()

    return ''.join(xff.split()) if xff else remote_addr

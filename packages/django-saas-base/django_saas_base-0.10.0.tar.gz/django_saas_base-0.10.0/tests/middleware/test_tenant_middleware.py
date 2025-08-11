from django.http import HttpResponse
from django.test import RequestFactory
from saas_base.middleware import TenantMiddleware
from saas_base.test import SaasTestCase


class TestTenantMiddleware(SaasTestCase):
    middleware_cls = TenantMiddleware

    @staticmethod
    def create_request(host):
        meta = {'HTTP_HOST': host}
        factory = RequestFactory(**meta)
        return factory.get('/')

    def setUp(self):
        self.middleware = self.middleware_cls(lambda req: HttpResponse())

    def test_match_cached_tenant(self):
        request = self.create_request('none.us.localhost')
        request.tenant_id = 1
        self.middleware(request)
        self.assertEqual(request.tenant, self.tenant)

    def test_missing_tenant_id(self):
        request = self.create_request('none.us.localhost')
        self.middleware(request)
        self.assertEqual(request.tenant, None)

    def test_not_found_tenant(self):
        request = self.create_request('none.us.localhost')
        request.tenant_id = 404
        self.middleware(request)
        self.assertEqual(request.tenant, None)

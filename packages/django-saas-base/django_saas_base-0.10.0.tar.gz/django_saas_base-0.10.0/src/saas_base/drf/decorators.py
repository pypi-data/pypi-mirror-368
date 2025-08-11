import functools


def resource_permissions(*names):
    """A decorator that adding required resource permissions to the view function.

    .. code-block:: python

        class TestView(Endpoint):
            @resource_permissions('tenant.admin')
            def post(self, request, *args, **kwargs):
                ...
    """

    def decorated(func):
        func._resource_permissions = names

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped

    return decorated

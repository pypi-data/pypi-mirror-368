from django.forms import model_to_dict
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings


def get_client_ip(request):
    """Получить ip клиента из request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class CurrentUserIdDefault:
    """Получить user_id из request для сериалайзера"""
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.id

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class ClientIpDefault:
    """Получить ip клиента из request для сериалайзера"""
    requires_context = True

    def __call__(self, serializer_field):
        return get_client_ip(serializer_field.context['request'])

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class PageSizePagination(PageNumberPagination):
    page_size_query_param = 'page_size'


class CustomJWTAuthentication(JWTAuthentication):
    def get_header(self, request):
        """
        Для авторизации с заголовком: Auth: Bearer 8e2928a5f341513728ee6870c57652582a3af99c
        """
        if request.META.get('HTTP_AUTH'):
            header = request.META.get('HTTP_AUTH')
        else:
            header = request.META.get(api_settings.AUTH_HEADER_NAME)
        if isinstance(header, str):
            header = header.encode(HTTP_HEADER_ENCODING)
        return header


class ModelDiffMixin:
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super().save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                                           self._meta.fields])

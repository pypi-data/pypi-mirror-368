from django.contrib import admin
from django.contrib.auth.models import Group, User
from rest_framework.authtoken.models import TokenProxy

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)

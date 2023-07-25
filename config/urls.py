"""config URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from . import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

# This is to return a JSON response instead of HTML template in case of any unhandled exceptions
# For more info: https://www.django-rest-framework.org/api-guide/exceptions/#generic-error-views
# DRF already handles 404 and 403 exceptions so no need the specify these.
# Note: this works only with DEBUG = False
handler500 = "rest_framework.exceptions.server_error"
handler404 = "rest_framework.exceptions.bad_request"

if settings.DEBUG:
    # Third Parties
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    urlpatterns += staticfiles_urlpatterns()

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views


urlpatterns = [
    ## general
    url(r'^admin/', admin.site.urls),
    ## social auth
    url(r'^accounts/login/$', auth_views.LoginView.as_view()),
    # url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include(('social_django.urls', 'social_django'), namespace='social')),
    url('', include(('django.contrib.auth.urls', 'django'), namespace='auth')),
]

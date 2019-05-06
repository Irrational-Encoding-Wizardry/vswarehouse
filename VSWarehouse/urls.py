"""VSWarehouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
import debug_toolbar
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path, include

import simple.views
import frontend.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('simple/', simple.views.overview, name="simple-overview"),

    path('simple/<project>/', simple.views.project, name="simple-project"),
    path('simple/<project>/<release>.py', simple.views.setup, name="simple-setup"),
    path('simple/<project>/<release>', simple.views.zip, name="simple-zip"),
    path('simple/<project>/<release>/<filename>.zip', simple.views.zip, name="simple-zip"),

    path('', frontend.views.listing, name="home"),
    path('faq/', frontend.views.static_page, name="faq", kwargs={'tab': 'faq', 'template': 'faq'}),
    path('impressum/', frontend.views.static_page, name="impressum", kwargs={'tab': 'impressum', 'template': 'impressum'}),
    path('privacy/', frontend.views.static_page, name="privacy", kwargs={'tab': 'privacy', 'template': 'privacy'}),

    path('search/', frontend.views.search, name="search"),
    path('plugins/<project>', frontend.views.plugin, name="plugin"),
    re_path('categories/(?P<category>.*)/', frontend.views.listing, name="category")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('__debug__', include(debug_toolbar.urls))
    ]

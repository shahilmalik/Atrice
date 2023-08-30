"""autolog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from pages.views import demo_view, track_view, latecomers, manage, enroll, delete_student, resetatt,dashboard_view,stop_demo_loop

urlpatterns = [
    path('admin/', admin.site.urls),
    path('demo/', demo_view, name='demo'),
    path('track/', track_view),
    path('latecomers/', latecomers,name="latecomers"),
    path('manage/', manage),
    path('enroll/', enroll),
    path('delete-student/<str:register_number>/', delete_student, name='delete_student'),
    path('resetatt/', resetatt),
    path('', dashboard_view, name='home'),
    path('dashboard/',dashboard_view),
    path('stop-demo-loop/', stop_demo_loop, name='stop_demo_loop')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

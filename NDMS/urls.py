"""NDMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from app01.myviews import epon_info_update,login_logout,query_by_crt,cutting,test,query_syslog

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('epon_create_update', epon_info_update.epon_create_update),
    path('login', login_logout.login),
    path('logout', login_logout.logout),
    path('query_crt', query_by_crt.query_crt),
    path('sql_cutting_query', cutting.sql_cutting_query),
    path('sql_syslog_query', query_syslog.sql_syslog_query),
    path('get_telnet_command/', query_by_crt.get_telnet_command),
    path('admin', admin.site.urls),
    path('test', test.test),
    path('', query_by_crt.query_crt),
]

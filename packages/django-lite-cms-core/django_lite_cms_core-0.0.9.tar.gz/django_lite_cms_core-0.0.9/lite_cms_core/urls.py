from django.contrib.auth.views import LogoutView
from django.urls import path

from lite_cms_core import views

app_name = 'lite_cms_core'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('extsearch/', views.ext_search_form, name='extsearch'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

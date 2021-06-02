from django.urls import path, re_path
from . import views

app_name='banco_dados'

urlpatterns = [
        re_path(r"lista/(?P<pk>[0-9]+)*[\/]*", views.ListView.as_view(), name='lista'),
        re_path(r'create/(?P<pk>[0-9]+)*[\/]*',views.CreateView.as_view(), name='create'),
        ]

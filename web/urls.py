from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^submit/expense/$', views.submit_expense, name='submit_expense'),
    # add any other URL patterns here
]
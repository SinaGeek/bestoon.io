from django.urls import re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    re_path(r'^submit/expense/$', views.submit_expense, name='submit_expense'),
    re_path(r'^submit/income/$', views.submit_income, name='submit_income'),
    re_path(r'^accounts/register/$', views.register, name='register'),
    re_path(r'^q/generalstat/$', views.generalstat, name='generalstat'),
    re_path(r'^accounts/logout/$', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    re_path(r'^$', views.index, name='index'),

    # add any other URL patterns here
]
"""csui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import re_path
from accounts.forms import PasswordChangeCustomForm
from crseed import views as crview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', crview.settingsView, name='index'),
]

urlpatterns += [
    path('crseed/settings', crview.settingsView,  name='home'),
    path('crseed/start', crview.proceedCrossSeed, name='cs_start'),
    path('crseed/settings', crview.settingsView,  name='cs_setting'),
    path('crseed/listtable', crview.CrossedTorrentTable.as_view(), name='cs_listtable'),
    path('crseed/list', crview.crossTorrentListView, name='cs_list'),
    path('crseed/historytable', crview.SearchHistoryTable.as_view(), name='cs_historytable'),
    path('crseed/history', crview.searchHistoryListView, name='cs_history'),
    # path('crseed/ajaxtable', crview.ajaxRefreshTorrentList, name='actor_table_ajax'),
    path('crseed/processlog', crview.ajaxRefreshProcessLog, name='process_log'),
    path('crseed/clearhistory', crview.clearHistory, name='cs_clear_history'),
    path('crseed/clearcrossed', crview.clearCrossed, name='cs_clearcrossed'),
    path('crseed/cancel_tasks', crview.cancelTasks, name='cs_cancel_tasks'),
    path('crseed/fix_path/<int:id>', crview.ajaxFixSeedPath, name='cs_fix_path'),
    path('crseed/delete_history/<int:id>', crview.ajaxDeleteHistory, name='cs_delete_history'),
]



urlpatterns += [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns += [
    re_path(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='auth/password_reset.html',
            email_template_name='auth/password_reset_email.html',
            subject_template_name='auth/password_reset_subject.txt'
        ),
        name='password_reset'),
    re_path(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
        name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'),
        name='password_reset_confirm'),
    re_path(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
        name='password_reset_complete'),

    re_path(r'^settings/password/$', auth_views.PasswordChangeView.as_view(template_name='auth/password_change.html', form_class=PasswordChangeCustomForm),
        name='password_change'),
    re_path(r'^settings/password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='auth/password_change_done.html'),
        name='password_change_done'),
]


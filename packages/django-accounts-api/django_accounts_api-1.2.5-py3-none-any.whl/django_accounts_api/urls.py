from django.urls import path

from . import views


app_name = 'django_accounts_api'
urlpatterns = [
    path('', views.APIManifest.as_view(), name='manifest'),

    path('check', views.APILoginCheck.as_view(), name='login_check'),
    path('login', views.APILogin.as_view(), name='login'),
    path('logout', views.APILogout.as_view(), name='logout'),

    path('password_change', views.APIPasswordChange.as_view(), name='password_change'),

    path('password_reset', views.APIPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.APIPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('users/', views.APIUsersView.as_view(), name='users'),
    path('user/<int:pk>/update', views.APIUserUpdate.as_view(), name='user_update'),
    path('user/<int:pk>/delete', views.APIUserDelete.as_view(), name='user_delete'),
    path('user/create', views.APIUserCreate.as_view(), name='user_create'),
    path('user/details', views.UserDetails.as_view(), name='user_details'),
    path('user/<int:pk>/reset', views.APIUserReset.as_view(), name='user_reset'),

    path('groups/', views.APIGroupsView.as_view(), name='groups'),
    path('group/create', views.APIGroupCreate.as_view(), name='group_create'),
    path('group/<int:pk>/update', views.APIGroupUpdate.as_view(), name='group_update'),
    path('group/<int:pk>/delete', views.APIGroupDelete.as_view(), name='group_delete'),

    path('membership/group/', views.APIMembershipGroupView.as_view(), name='membership_groups'),
    path('membership/group/<int:group_id>', views.APIMembershipGroupView.as_view(), name='membership_group'),
    path('membership/group/<int:group_id>/<int:user_id>', views.APIMembershipUserView.as_view(), name='membership_group_join'),
    path('membership/user/', views.APIMembershipUserView.as_view(), name='membership_users'),
    path('membership/user/<int:user_id>', views.APIMembershipUserView.as_view(), name='membership_user'),
    path('membership/user/<int:user_id>/<int:group_id>', views.APIMembershipUserView.as_view(), name='membership_user_join'),

    path('permissions/', views.APIPermissionsView.as_view(), name='permissions'),
    path('permissions/group/<int:group_id>/<int:permission_id>', views.APIGroupPermissionCreate.as_view(), name='group_permission_create'),
    path('permissions/user/<int:user_id>/<int:permission_id>', views.APIUserPermissionCreate.as_view(), name='user_permission_create'),
    path('permissions/group/remove/<int:group_id>/<int:permission_id>', views.APIGroupPermissionDelete.as_view(), name='group_permission_delete'),
    path('permissions/user/remove/<int:user_id>/<int:permission_id>', views.APIUserPermissionDelete.as_view(), name='user_permission_delete'),
]

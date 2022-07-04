from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('login_auth/', views.login_auth, name='login_auth'),
    path('not_found', views.not_found, name='not_found'),
    path('user_not_found', views.user_not_found, name='user_not_found'),
    path('users',views.users,name='users'),
    path('logout',views.userlogout,name='userlogout'),
    path('switch_role/<int:group_id>',views.switch_role,name="switch_role"),
    path('create_role/<str:id>',views.create_role,name="create_role"),
    path('update_role/<str:id>',views.update_role,name="update_role"),
    path('delete_role/<str:id>',views.delete_role,name="delete_role"),
    path('pab_user_login/<str:email>',views.pab_user_login,name='pab_user_login'),
    path('my_profile',views.my_profile,name='my_profile'),
    path('url_encode', views.url_encode, name='url_encode'),
    path('allstaff', views.allstaff, name='staff'),
    path('session/<str:id>', views.session, name='session'),
    path('update_u_codes/', views.update_u_codes, name='update_u_codes'),
]
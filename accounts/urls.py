from django.urls import path
from accounts import views


urlpatterns = [

    path('user_login/', views.user_login, name='user_login'),
    path('user-signup/', views.user_signup, name='user_signup'),
    path('logout/', views.logout, name='user_logout'),
    path('AddCheckoutAddress/', views.AddCheckoutAddress, name='AddCheckoutAddress'),
    path('deleteCheckoutAddress/<int:id>/', views.deleteCheckoutAddress, name='deleteCheckoutAddress'),
    path('editAddress/<int:id>/', views.editAddress, name='editAddress'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('change-password/', views.change_password, name='change_password'),
    path('myAddress/', views.myAddress, name='myAddress'),
    path('addAddress/', views.addAddress,name='addAddress'),
    path('deleteAddress/<int:id>/', views.deleteAddress,name='deleteAddress'),
    path('add_amount/', views.add_amount,name='add_amount'),
]   

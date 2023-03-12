from django.urls import path
from .import views

urlpatterns = [
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('', views.adminhome, name='adminhome'),
    path('adminlogout/', views.adminlogout, name='adminlogout'),
    path('adminproduct/', views.adminproduct, name='adminproduct'),
    path('admin-addproducts/', views.admin_addproducts, name='admin_addproducts'),
    path('admin-category/', views.admin_category, name='admin_category'),
    path('admin-addcategory/', views.admin_addcategory, name='admin_addcategory'),
    path('admin-subcategory/', views.admin_subcategory, name='admin_subcategory'),
    path('admin-addsubcategory/', views.admin_addsubcategory, name='admin_addsubcategory'),
    path('admin-userlist/', views.admin_userlist, name='admin_userlist'),
    path('<int:id>/admin-deletecategory/', views.admin_deletecategory, name='admin_deletecategory'),
    path('<int:id>/update-category/', views.update_category, name='update_category'),
    path('<int:id>/admin-deletesubcategory/', views.admin_deletesubcategory, name='admin_deletesubcategory'),
    path('<int:id>/blockuser/', views.blockuser, name='blockuser'),
    path('<int:id>/update-products/', views.update_products,name='update_products'),
    path('<int:id>/delete-products/', views.delete_products,name='delete_products'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('update-order/<int:id>',views.update_order,name="update_order"),
    path('coupon/', views.coupon,name='coupon'),
    path('addCoupon/', views.addCoupon,name='addCoupon'),
    path('<int:id>/deleteCoupon/', views.deleteCoupon,name='deleteCoupon'),
    path('<int:id>/updateCoupon/', views.updateCoupon,name='updateCoupon'),
    
    

    



]

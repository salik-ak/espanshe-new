from django.urls import path
from .import views

urlpatterns = [
    path('store/', views.user_products, name='user_products'),
    path('store/<slug:product_slug>/', views.user_productdetails, name='user_productdetails'),
    path('category/<slug:sub_category_slug>/', views.products_by_sub_category,name='products_by_sub_category'),
    path('search/', views.search, name='search'),
]
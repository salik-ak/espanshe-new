from django.urls import path
from order import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path("cash-on-delivery/<int:id>/",views.cash_on_delivery,name='cash_on_delivery'),
    path('payments/', views.payments, name='payments'),
    path('order-complete/', views.order_complete, name='order_complete'),
    path("cancel-order/<int:id>/",views.cancel_order,name='cancel_order'),
    path("return-order/<int:id>/",views.return_order,name='return_order'),
    path("coupons/",views.coupons,name='coupons'),
    path('wallet/<int:id>/', views.wallet,name='wallet'),
]

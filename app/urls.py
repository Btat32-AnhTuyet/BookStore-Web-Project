from django.contrib import admin
from django.urls import path
from.import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('search/', views.search, name="search"),
    path('category/', views.category, name="category"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('cart/', views.cart, name="cart"),
    path('detail/', views.detail, name="detail"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('profile/', views.profile, name='profile'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('path/to/create_paypal_transaction/', views.create_paypal_transaction, name='create_paypal_transaction'),
]

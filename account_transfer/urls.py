from django.urls import path

from . import views

urlpatterns = [
    path('', views.AccountView.as_view(), name='List Accounts'),
    path('<uuid:id>/', views.AccountView.as_view(), name='Account Details'),
]

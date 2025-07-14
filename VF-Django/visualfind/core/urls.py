from django.urls import path
from . import views
urlpatterns = [
    path('', views.index_view, name='index'),
    path('upload/', views.upload_view, name='upload'),
    path('all-products/', views.all_products_view, name='all_products'),
]
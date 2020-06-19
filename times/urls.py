from django.urls import path

from .import views

app_name = 'times'
urlpatterns = [
    path('days', views.IndexView.as_view(), name="index"),
    path('days/<int:pk>/', views.DetailView.as_view(), name="detail"),
    path('days/create/', views.DayCreate.as_view(), name="day_create"),
    path('days/<int:pk>/items/create', views.ItemCreate.as_view(), name="item_create"),
    # path('days/<int:pk>/items/<int:pk>/', views.ItemUpdate.as_view(), name="item_update"),
]

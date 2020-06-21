from django.urls import path

from .import views

app_name = 'times'
urlpatterns = [
    path('days', views.IndexView.as_view(), name="index"),
    path('days/<int:pk>/', views.DetailView.as_view(), name="detail"),
    path('days/create/', views.DayCreate.as_view(), name="day_create"),
    path('days/<int:pk>/items/add',
         views.ItemCreate.as_view(), name="items_create"),
    path('days/generate_days', views.gen_batch_days, name="gen_batch_days"),
]

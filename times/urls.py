from django.urls import path

from .import views

app_name = 'times'
urlpatterns = [
    path('', views.YearMonthListView.as_view(), name="year_months"),
    path('year_month/create/', views.YearMonthCreate.as_view(), name='year_month_create'),
    path('year_month/<int:pk>/update/',
         views.YearMonthUpdate.as_view(), name='year_month_update'),
    path('year_month/<int:pk>/delete/',
         views.YearMonthDelete.as_view(), name='year_month_delete'),
]

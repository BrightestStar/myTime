from django.urls import path, re_path

from .import views

app_name = 'times'
urlpatterns = [
    path('', views.YearMonthListView.as_view(), name="year_months"),
    path('year_month/create/', views.YearMonthCreate.as_view(), name='year_month_create'),
    path('year_month/<int:pk>/update/',
         views.YearMonthUpdate.as_view(), name='year_month_update'),
    path('year_month/<int:pk>/delete/',
         views.YearMonthDelete.as_view(), name='year_month_delete'),
    path('month_detail/<int:pk>',
         views.MonthDetailView.as_view(), name="month_detail"),
]
urlpatterns += [
    path('weeks/<int:pk>/detail/number/<int:number>', views.WeekDetailView.as_view(), name="week_detail"),
    path('days/<int:pk>/detail/', views.DayDetailView.as_view(), name="day_detail"),
    path('year_month/<int:pk>/generate_days/<int:number>',
         views.generate_days, name='generate_days'),
]
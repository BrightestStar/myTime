from django.contrib import admin

from .models import YearMonth, Day, Item, Category, TimePlan

admin.site.register(Day)
admin.site.register(TimePlan)
admin.site.register(YearMonth)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cname', 'alias', 'time_entry')


@admin.register(Item)
class ItmeAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'cname', 'pub_date')

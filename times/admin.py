from django.contrib import admin

from .models import Day, Item, Category

admin.site.register(Day)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cname', 'alias', 'time_entry')


@admin.register(Item)
class ItmeAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'cname', 'pub_date')

from django.contrib import admin

from .models import User, Day, Item

admin.site.register(Day)
admin.site.register(User)
admin.site.register(Item)

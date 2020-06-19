from django.contrib import admin

from .models import User
from .models import Day

admin.site.register(Day)
admin.site.register(User)

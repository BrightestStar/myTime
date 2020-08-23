from django.db.models import Sum
from django.db import models
from django.contrib.auth.models import User


class YearMonth(models.Model):
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=2)

    @property
    def y_m(self):
        return f'{self.year} - {self.month}'

    def __str__(self):
        return self.y_m
        


class Day(models.Model):
    year_month = models.ForeignKey('YearMonth', on_delete=models.SET_NULL, null=True)
    recorder = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    day_name = models.CharField(max_length=200)
    time_entry = models.DecimalField(decimal_places=2, max_digits=6, blank=True)
    pub_date = models.DateField()
    begin_time = models.TimeField()

    def __str__(self):
        return self.day_name


class Category(models.Model):
    cname = models.CharField(max_length=200)
    alias = models.CharField(max_length=200)

    def __str__(self):
        return self.cname

    @property
    def time_entry(self):
        subtotal = self.item_set.all().aggregate(Sum('duration'))
        return subtotal.get('duration__sum')

class TimePlan(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # the unit of duration is mintue
    duration = models.IntegerField()
    begin_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{begin_date}~{end_date}#{self.category.cname}-estimate'

class Item(models.Model):
    item_name = models.CharField(max_length=200)
    duration = models.DecimalField(decimal_places=2, max_digits=64)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    pub_date = models.DateField()
    year_month = models.ForeignKey(
        'YearMonth', on_delete=models.SET_NULL, null=True)

    def cname(self):
        return self.category.cname

    def __str__(self):
        return self.item_name




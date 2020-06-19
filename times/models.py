from django.db import models

class User(models.Model):
    username = models.CharField(max_length=200)

    def __str__(self):
        return self.username


class Day(models.Model):
    day_name = models.CharField(max_length=200)
    time_entry = models.DecimalField(decimal_places=2, max_digits=64)
    pub_date = models.DateTimeField('date pubilshed')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.day_name


class Item(models.Model):
    item_name = models.CharField(max_length=200)
    duration = models.DecimalField(decimal_places=2, max_digits=64)
    user = models.ForeignKey(Day, on_delete=models.CASCADE)

    def __str__(self):
        return self.item_name

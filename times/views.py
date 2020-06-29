from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect
from django.template import loader

from .models import Day, Item, YearMonth

# import the current file settings
from .settings import DIR_PATH
# for create object
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.views import generic
from django.urls import reverse, reverse_lazy
# for read files
from django.core.files import File

import glob



class DetailView(generic.DetailView):
    model = Day
    template_name = 'times/detail.html'


class YearMonthListView(generic.ListView):
    model = YearMonth


class YearMonthCreate(CreateView):
    model = YearMonth
    fields = '__all__'
    success_url = reverse_lazy('times:year_months')


class YearMonthUpdate(UpdateView):
    model = YearMonth
    fields='__all__'
    success_url = reverse_lazy('times:year_months')


class YearMonthDelete(DeleteView):
    model = YearMonth
    success_url = reverse_lazy('times:year_months')



def read_html(request, yy, mm):
    dir_path = DIR_PATH
    files = glob.glob(dir_path % (yy, mm))
    print(files)




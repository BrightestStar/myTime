from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect
from django.template import loader

from .models import Day, Item

# import the current file settings
from .settings import DIR_PATH
# for create object
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.views import generic
from django.urls import reverse, reverse_lazy
# for read files
from django.core.files import File

import glob


class DayCreate(CreateView):
    model = Day
    fields = '__all__'


class ItemCreate(CreateView):
    model = Item
    fields = '__all__'
    template_name = 'times/items/item_form.html'

    def items_create(self, request):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(request)
        model = Day
        template_name = 'times/detail.html'

        # return HttpResponseRedirect(reverse('times:detail', args=('2')))

    
class ItemUpdate(UpdateView):
    model = Item
    fields = ['item_name', 'duration']



class IndexView(generic.ListView):
    template_name = 'times/index.html'
    context_object_name = 'latest_days_list'

    def get_queryset(self):
        return Day.objects.order_by('-pub_date')[:7]


class DetailView(generic.DetailView):
    model = Day
    template_name = 'times/detail.html'


def read_html(request, yy, mm):
    dir_path = DIR_PATH
    files = glob.glob(dir_path % (yy, mm))
    print(files)


def gen_batch_days(request):
    sasdf


def gen_batch_items(request, day_id):
    asdfa




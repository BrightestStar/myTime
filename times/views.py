from datetime import datetime
import re, os, time
import codecs as cs
from bs4 import BeautifulSoup
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


class YearMonthListView(generic.ListView):
    model = YearMonth


class YearMonthCreate(CreateView):
    model = YearMonth
    fields = '__all__'
    success_url = reverse_lazy('times:year_months')


class YearMonthUpdate(UpdateView):
    model = YearMonth
    fields = '__all__'
    success_url = reverse_lazy('times:year_months')


class YearMonthDelete(DeleteView):
    model = YearMonth
    success_url = reverse_lazy('times:year_months')


class MonthDetailView(generic.DetailView):
    model = YearMonth

    def get_context_data(self, **kwargs):
        context = super(MonthDetailView, self).get_context_data(**kwargs)
        context['day_list'] = Day.objects.filter(year_month=self.object).extra(
            select={'day_number': 'CAST(day_name AS INTEGER)'}
        ).order_by('day_number')
        
        return context


def generate_days(request, pk):
    # statistic time for this function
    t_1 = datetime.now()

    recorder = request.user
    year_month = YearMonth.objects.get(pk=pk)
    yy, mm = int(year_month.year), int(year_month.month)

    # read files the type of html on local
    dir_path = DIR_PATH % (yy, mm)
    files = glob.glob(dir_path)
    for idx_f, file in enumerate(files):
        file_name = os.path.basename(file)
        params = dict()
        grant_time = 0

        if file_name != 'index.html':
            file_content = cs.open(file, 'r', 'utf-8').read()
            document = BeautifulSoup(file_content, 'html.parser').get_text()
            reset_doc = document.split('。')

            # generate day by the head information
            # or generate items by the body information
            for idx, item_text in enumerate(reset_doc):
                if idx == 0:
                    month, dd, hh, mi = re.findall(r'\d+', item_text)
                    if int(month) == mm:
                        params['day_name'] = f'{dd}/{mm}/{yy}'
                        params['begin_time'] = datetime.strptime(
                            f'{yy}/{mm}/{dd} {hh}:{mi}', '%Y/%m/%d %H:%M').strftime("%H:%M")
                        params['recorder'] = recorder
                        params['year_month'] = year_month
                        day = Day(**params)
                else:
                    try:
                        *item_name, duration = item_text.replace('分钟', '').split('：')
                        item = Item(item_name='#'.join(item_name),
                                    duration=duration, day=day)
                        item.save()
                        grant_time += int(duration)
                    except:
                        item_text
                day.time_entry = grant_time
                day.save()
    t_2 = datetime.now() - t_1
    print(t_2)
    return HttpResponseRedirect(reverse('times:month_detail', args=[pk]))


class DayDetailView(generic.DetailView):
    model = Day
    template_name = 'times/day_detail.html'
    

class WeekDetailView(generic.DetailView):
    model = YearMonth
    template_name = 'times/week_detail.html'

    def get_context_data(self, **kwargs):
        start_day, end_day = which_week(self.kwargs['number'])

        context = super(WeekDetailView, self).get_context_data(**kwargs)
        context['day_list'] = Day.objects.filter(year_month=context.get('object')).extra(
            select={'day_number': 'CAST(day_name AS INTEGER)'}
        ).order_by('day_number')[start_day:end_day]
        return context


def which_week(number):
    if int(number) == 0:
        return 0, 7
    elif int(number) == 1:
        return 7, 14
    elif int(number) == 2:
        return 15, 21
    elif int(number) == 3:
        return 22, 31

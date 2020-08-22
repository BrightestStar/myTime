import numpy as np
from chartjs.views.lines import BaseLineChartView
from datetime import datetime
import re, os, time, re
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


def generate_days(request, pk, **kwargs):
    # statistic time for this function
    t_1 = datetime.now()

    recorder = request.user
    year_month = YearMonth.objects.get(pk=pk)
    yy, mm = int(year_month.year), int(year_month.month)

    # read files the type of html on local
    number = kwargs['number']
    files = obtain_files(yy, mm, number)

    if len(files) <= 0:
        return HttpResponseRedirect(reverse('times:month_detail', args=[pk]))

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
                    try: 
                        Day.objects.filter(day_name=f'{dd}/{mm}/{yy}', year_month=year_month).delete()
                    except:
                        print('Dose Not Exist object')

                    if int(month) == mm:
                        params['day_name'] = f'{dd}/{mm}/{yy}'
                        params['begin_time'] = datetime.strptime(
                            f'{yy}/{mm}/{dd} {hh}:{mi}', '%Y/%m/%d %H:%M').strftime("%H:%M")
                        params['recorder'] = recorder
                        params['year_month'] = year_month
                        day = Day(**params)
                    else:
                        return HttpResponseRedirect(reverse('times:month_detail', args=[pk]))
                else:
                    try:
                        *item_name, duration = item_text.replace('分钟', '').split('：')
                        item = Item(item_name='#'.join(
                            item_name), duration=duration, day=day, year_month=year_month)
                        item.save()
                        grant_time += int(duration)
                    except:
                        item_text
                day.time_entry = grant_time
                day.save()
    t_2 = datetime.now() - t_1
    print(t_2)
    return HttpResponseRedirect(reverse('times:month_detail', args=[pk]))


def obtain_files(yy, mm, number):
    start_day, end_day = which_week(number)
    dir_path = DIR_PATH % (yy, mm)
    files = [file for file in glob.glob(dir_path) if "index.html" not in file]
    return sorted(files, key=file_title)[start_day:end_day]


def file_title(filename):
    pattern = re.compile(r'(\d+)')
    return int(pattern.findall(filename)[-1])


class DayDetailView(generic.DetailView):
    model = Day
    template_name = 'times/day_detail.html'
    

class WeekDetailView(generic.DetailView):
    model = YearMonth
    template_name = 'times/week_detail.html'

    def get_context_data(self, **kwargs):
        start_day, end_day = which_week(self.kwargs['number'])

        context = super(WeekDetailView, self).get_context_data(**kwargs)
        context['number'] = self.kwargs['number']
        context['day_list'] = Day.objects.filter(year_month=kwargs['object']).extra(
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
    elif int(number) == 6:
        return 0, 31


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        return list(self.sort_data().keys())

    def get_providers(self):
        results = []
        year_month_pk, number = self.week_number()
        year_month_name = YearMonth.objects.get(pk=year_month_pk).y_m

        results.append('%s#%s :' % (year_month_name, number))
        
        return results


    def get_data(self):
        results = []
        percent = 0
        total = sum(list(self.sort_data().values()))
        for value in list(self.sort_data().values()):
            percent += value/total
            results.append(round(percent*100, 2))

        return [results]


    def sort_data(self):
        names = []
        results = dict()
        days = self.obtain_days()

        for day in days:
            for item in day.item_set.all():
                if item.item_name not in names:
                    names.append(item.item_name)

        for day in days:
            for item in day.item_set.all():
                results[item.item_name] = results.get(item.item_name, 0) + item.duration

        results = {k: v for k, v in sorted(
            results.items(), key=lambda item: item[1], reverse=True)}

        return results

    def obtain_days(self):
        year_month_pk, number = self.week_number()
        start_day, end_day = which_week(number)
        year_month = YearMonth.objects.filter(pk=year_month_pk)

        return Day.objects.filter(year_month__in=year_month).extra(
            select={'day_number': 'CAST(day_name AS INTEGER)'}
        ).order_by('day_number')[start_day:end_day]


    def week_number(self):
        # numebr which is the weeks's serial number
        year_month_pk = self.request.GET.get('weeks')
        number = self.request.GET.get('number')

        return year_month_pk, number

line_chart_json = LineChartJSONView.as_view()

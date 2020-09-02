from django.db.models import Sum
import numpy as np
from chartjs.views.lines import BaseLineChartView
from datetime import datetime, date
import re, os, time, re
import codecs as cs
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect
from django.template import loader, Library

from .models import Day, Item, YearMonth, Category, TimePlan

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


class EstimateCreate(CreateView):
    model = TimePlan
    fields = '__all__'

    def get_initial(self):
        initial = super(EstimateCreate, self).get_initial()
        yearmonth = YearMonth.objects.get(pk=self.kwargs['pk'])
        bday, eday = which_week(self.kwargs['number'])
        begin_date, end_date = b_e_date(
            yearmonth.year, yearmonth.month, bday, eday)
        initial.update({'begin_date': begin_date,
                        'end_date': end_date})
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        pk, number = self.kwargs['pk'], self.kwargs['number']
        return HttpResponseRedirect(reverse('times:week_detail', args=[pk, number]))


class EstimateInfo(generic.DetailView):
    model = YearMonth
    template_name = 'times/time_plans.html'

    def get_context_data(self, **kwargs):
        begin_number, end_number = which_week(self.kwargs['number'])
        begin_date = b_e_date(self.object.year, self.object.month, begin_number, end_number)[0]
        context = super(EstimateInfo, self).get_context_data(**kwargs)
        context['time_plans'] = TimePlan.objects.filter(begin_date=begin_date)
        context['params'] = {'pk': self.object.pk,
                             'number': self.kwargs['number']}

        return context

class EstimateUpdate(UpdateView):
    model = TimePlan
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('times:week_detail', kwargs={'pk': self.kwargs['ym_pk'], 'number': self.kwargs['number']})


class CategoryDetail(generic.ListView):
    model = Category

    def get_context_data(self, **kwargs):
        begin_number, end_number = which_week(self.kwargs['number'])
        y_m = YearMonth.objects.get(pk=self.kwargs['ym_pk'])
        begin_date, end_date = b_e_date(
            y_m.year, y_m.month, begin_number, end_number)
        context = super(CategoryDetail, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.filter(
            alias=self.kwargs['key'])
        context['params'] = {'pk': y_m.pk,
                             'number': self.kwargs['number'],
                             'begin_date': begin_date,
                             'end_date': end_date,
                             }

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
                        Day.objects.filter(day_name=f'{dd}/{mm}/{yy}').delete()
                    except:
                        print('Dose Not Exist object')

                    if int(month) == mm:
                        params['day_name'] = f'{dd}/{mm}/{yy}'
                        params['begin_time'] = datetime.strptime(
                            f'{yy}/{mm}/{dd} {hh}:{mi}', '%Y/%m/%d %H:%M').strftime("%H:%M")
                        params['recorder'] = recorder
                        params['year_month'] = year_month
                        params['pub_date'] = datetime.strptime(
                            f'{yy}/{mm}/{dd}', '%Y/%m/%d')
                        day = Day(**params)
                    else:
                        return HttpResponseRedirect(reverse('times:month_detail', args=[pk]))
                else:
                    try:
                        *item_name, duration = item_text.replace('分钟', '').split('：')
                        item_name = '#'.join(item_name)
                        category = classify(item_name)
                        item = Item(item_name=item_name, duration=duration, day=day,
                                    year_month=year_month, category=category, pub_date=day.pub_date)
                        item.save()
                        grant_time += int(duration)
                    except:
                        item_text
                day.time_entry = grant_time
                day.save()
    t_2 = datetime.now() - t_1
    print(t_2)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def obtain_files(yy, mm, number):
    begin_day, end_day = which_week(number)
    dir_path = DIR_PATH % (yy, mm)
    files = [file for file in glob.glob(dir_path) if "index.html" not in file]
    return sorted(files, key=file_title)[begin_day:end_day]


def file_title(filename):
    pattern = re.compile(r'(\d+)')
    return int(pattern.findall(filename)[-1])

def classify(name):
    pre_name = name.split('@')[0]
    category = Category.objects.filter(cname=pre_name)
    if not category.exists() and pre_name:
        category = Category(cname=pre_name, alias=pre_name)
        category.save()

    return Category.objects.get(cname=pre_name)

class DayDetailView(generic.DetailView):
    model = Day
    template_name = 'times/day_detail.html'
    

class WeekDetailView(generic.DetailView):
    model = YearMonth
    template_name = 'times/week_detail.html'

    def get_context_data(self, **kwargs):
        begin_day, end_day = which_week(self.kwargs['number'])

        context = super(WeekDetailView, self).get_context_data(**kwargs)
        context['number'] = self.kwargs['number']
        context['day_list'] = Day.objects.filter(year_month=kwargs['object']).extra(
            select={'day_number': 'CAST(day_name AS INTEGER)'}
        ).order_by('day_number')[begin_day:end_day]
        context['subtotals'], context['estimates'] = subtotals(
            kwargs['object'].year, kwargs['object'].month, begin_day, end_day)
        return context


def subtotals(yy, mm, bday, eday):
    begin_date, end_date = b_e_date(yy, mm, bday, eday)
    results = {}
    estimates = {}
    clist = Category.objects.all().values_list('alias', flat=True)
    for alias in set(list(clist)):
        for c in Category.objects.filter(alias=alias):
            items = c.item_set.filter(
                pub_date__range=[begin_date, end_date])
            results[alias] = results.get(
                alias, 0) + sum(items.values_list('duration', flat=True))
            plans = c.timeplan_set.filter(begin_date=begin_date).distinct()
            estimates[alias] = estimates.get(
                alias, 0) + sum(plans.values_list('duration', flat=True))

    results = {k: v for k, v in sorted(
        results.items(), key=lambda item: item[1], reverse=True)}
    estimates = {k: v for k, v in sorted(
        estimates.items(), key=lambda item: item[1], reverse=True)}

    return results, estimates

# generate begin and end date
def b_e_date(yy, mm, bday, eday):
    yy, mm, bday, eday= int(yy), int(mm), int(bday+1), int(eday)
    begin_date = date(yy, mm, bday)
    try:
        end_date = date(yy, mm, eday)
    except:
        end_date = date(yy, mm, eday-1)

    return begin_date, end_date

def which_week(number):
    if int(number) == 0:
        return 0, 7
    elif int(number) == 1:
        return 7, 14
    elif int(number) == 2:
        return 14, 21
    elif int(number) == 3:
        return 21, 31
    elif int(number) == 6:
        return 0, 31

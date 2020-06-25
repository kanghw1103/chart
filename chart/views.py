#  chart/views.py
from django.shortcuts import render
from .models import Passenger
from django.db.models import Count, Q
import json
from django.http import JsonResponse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker


def home(request):
    return render(request, 'home.html')


def world_population(request):
    return render(request, 'world_population.html')


def ticket_class_view_1(request):  # 방법 1
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(
            survived_count=Count('ticket_class',
                                 filter=Q(survived=True)),
            not_survived_count=Count('ticket_class',
                                     filter=Q(survived=False))) \
        .order_by('ticket_class')
    return render(request, 'ticket_class_1.html', {'dataset': dataset})


def ticket_class_view_2(request):  # 방법 2
    df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv', parse_dates=['Date'])
    countries = ['Korea, South', 'Germany', 'United Kingdom', 'US', 'France']
    df = df[df['Country'].isin(countries)]
    df['Cases'] = df[['Confirmed', 'Recovered', 'Deaths']].sum(axis=1)
    df = df.pivot(index='Date', columns='Country', values='Cases')
    countries = list(df.columns)
    covid = df.reset_index('Date')
    covid.set_index(['Date'], inplace=True)
    covid.columns = countries
    populations = {'Korea, South': 51269185, 'Germany': 83783942, 'United Kingdom': 67886011, 'US': 331002651,
                   'France': 65273511}
    percapita = covid.copy()
    for country in list(percapita.columns):
        percapita[country] = percapita[country] / populations[country] * 1000000

    colors = {'Korea, South': '#045275', 'France': '#7CCBA2', 'Germany': '#FCDE9C', 'US': '#DC3977',
              'United Kingdom': '#7C1D6F'}
    plt.style.use('fivethirtyeight')
    # 원 코드의 선과 레이블 색상이 맞지 않는 문제를 해결한 코드
    # for country in countries:
    #     plot = percapita[country].plot(figsize=(12, 8), color=colors[country], linewidth=5, legend=False)
    #
    # plot.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    # plot.grid(color='#d4d4d4')
    # plot.set_xlabel('Date')
    # plot.set_ylabel('# of Cases per 1,000,000 People')
    # for country in list(colors.keys()):
    #     plot.text(x=covid.index[-1], y=covid[country].max(),
    #               color=colors[country], s=country, weight='bold')


    # 빈 리스트 5종 준비
    france_data = list()
    germany_data = list()
    korea_South_data = list()
    us_data = list()
    united_Kingdom_data = list()


    # 리스트 5종에 형식화된 값을 등록
    for entry in percapita.index:
        france_data.append(entry["France"])
        germany_data.append(entry['Germany'])
        korea_South_data.append(entry['Korea, South'])
        us_data.append(entry['US'])
        united_Kingdom_data.append(entry['United Kingdom'])


    France = {
        'name': 'France',
        "type": "spline",
        "yAxis": 1,
        'data': france_data,
        'color': 'green',
    }

    Germany = {
        'name': 'Germany',
        "type": "spline",
        "yAxis": 1,
        'data': germany_data,
        'color': 'red',
    }

    Korea_South = {
        'name': 'Korea_South',
        'type': 'spline',
        'data': korea_South_data,
        'color': 'skyblue',
    }

    US = {
        'name': 'US',
        'type': 'spline',
        'data': us_data,
        'color': 'skyblue',
    }

    United_Kingdom = {
        'name': 'United_Kingdom',
        'type': 'spline',
        'data': united_Kingdom_data,
        'color': 'skyblue',
    }

    chart = {
        'chart': {'type': 'spline'},
        'title': {'text': 'COVID-19 확진자 발생율'},
        'xAxis': {'type': "datetime"},
        "yAxis": [{"labels": {"format": "{value} 건/백만 명", "style": {"color": "blue"}},
                   "title": {"text": "합계건수", "style": {"color": "blue"}}}],
        "tooltip": {"shared": "true"},
        'series': [France, Germany, Korea_South, US, United_Kingdom]
    }
    dump = json.dumps(chart)

    return render(request, 'ticket_class_2.html', {'chart': dump})


def ticket_class_view_3(request):  # 방법 3
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
                  not_survived_count=Count('ticket_class', filter=Q(survived=False))) \
        .order_by('ticket_class')

    # 빈 리스트 3종 준비 (series 이름 뒤에 '_data' 추가)
    categories = list()                 # for xAxis
    survived_series_data = list()       # for series named 'Survived'
    not_survived_series_data = list()   # for series named 'Not survived'
    survived_rate_data = list()

    # 리스트 3종에 형식화된 값을 등록
    for entry in dataset:
        categories.append('%s Class' % entry['ticket_class'])         # for xAxis
        survived_series_data.append(entry['survived_count'])          # for series named 'Survived'
        not_survived_series_data.append(entry['not_survived_count'])  # for series named 'Not survived'
        survived_rate_data.append(entry['survived_count']/(entry['survived_count']+entry['not_survived_count'])*100)

    survived_series = {
        'name': '생존',
        "type": "column",
        "yAxis": 1,
        'data': survived_series_data,
        'color': 'green',
        "tooltip": {"valueSuffix": " 명"}
    }
    not_survived_series = {
        'name': '비 생존',
        "type": "column",
        "yAxis": 1,
        'data': not_survived_series_data,
        'color': 'red',
        "tooltip": {"valueSuffix": " 명"}
    }
    survived_rate = {
        'name': '생존율',
        'type': 'spline',
        'data': survived_rate_data,
        'color': 'skyblue',
        "tooltip": {"valueSuffix": " %"}
    }

    chart = {
        'chart': {'zoomType': 'xy'},
        'title': {'text': '좌석 등급에 따른 타이타닉 생존/비 생존 인원 및 생존율'},
        'xAxis': {'categories': categories},
        "yAxis": [{"labels": {"format": "{value} %", "style": {"color": "blue"}},
                   "title": {"text": "생존율", "style": {"color": "blue"}}},
                  {"labels": {"format": "{value} 명", "style": {"color": "black"}},
                   "title": {"text": "인원", "style": {"color": "black"}}, "opposite": "true"}],
        "tooltip": {"shared": "true"},
        'series': [survived_series, not_survived_series, survived_rate]
    }
    dump = json.dumps(chart)

    return render(request, 'ticket_class_3.html', {'chart': dump})


def json_example(request):  # 접속 경로 'json-example/'에 대응하는 뷰
    return render(request, 'json_example.html')


def chart_data(request):  # 접속 경로 'json-example/data/'에 대응하는 뷰
    dataset = Passenger.objects \
        .values('embarked') \
        .exclude(embarked='') \
        .annotate(total=Count('id')) \
        .order_by('-total')
    #  [
    #    {'embarked': 'S', 'total': 914}
    #    {'embarked': 'C', 'total': 270},
    #    {'embarked': 'Q', 'total': 123},
    #  ]

    # # 탑승_항구 상수 정의
    # CHERBOURG = 'C'
    # QUEENSTOWN = 'Q'
    # SOUTHAMPTON = 'S'
    # PORT_CHOICES = (
    #     (CHERBOURG, 'Cherbourg'),
    #     (QUEENSTOWN, 'Queenstown'),
    #     (SOUTHAMPTON, 'Southampton'),
    # )
    port_display_name = dict()
    for port_tuple in Passenger.PORT_CHOICES:
        port_display_name[port_tuple[0]] = port_tuple[1]
    # port_display_name = {'C': 'Cherbourg', 'Q': 'Queenstown', 'S': 'Southampton'}

    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': 'Number of Titanic Passengers by Embarkation Port'},
        'series': [{
            'name': 'Embarkation Port',
            'data': list(map(
                lambda row: {'name': port_display_name[row['embarked']], 'y': row['total']},
                dataset))
            # 'data': [ {'name': 'Southampton', 'y': 914},
            #           {'name': 'Cherbourg', 'y': 270},
            #           {'name': 'Queenstown', 'y': 123}]
        }]
    }
    # [list(map(lambda))](https://wikidocs.net/64)

    return JsonResponse(chart)
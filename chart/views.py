#  chart/views.py
from django.shortcuts import render
from .models import Passenger
from django.db.models import Count, Q
import json
from django.http import JsonResponse
import pandas as pd
import arrow


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


def covid19_view(request):  # 방법 2
    # Section 2 - Loading and Selecting Data
    df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv',
                     parse_dates=['Date'])

    countries = ['Korea, South', 'Germany', 'United Kingdom', 'US', 'France']
    df = df[df['Country'].isin(countries)]

    df['Cases'] = df[['Confirmed']].sum(axis=1)

    df = df.pivot(index='Date', columns='Country', values='Cases')

    countries = list(df.columns)
    # df.reset_index()를 통하여 기존 인덱스 열을 데이터 열로 변경
    covid = df.reset_index('Date')
    # covid 인덱스와 columns를 새로 지정
    covid.set_index(['Date'], inplace=True)
    covid.columns = countries
    # print(covid.head())


    populations = {'Korea, South': 51269185, 'Germany': 83783942, 'United Kingdom': 67886011, 'US': 331002651,
                   'France': 65273511}
    percapita = covid.copy()
    for country in list(percapita.columns):
        percapita[country] = percapita[country] / populations[country] * 1000000

    my_data = list()
    for country in list(percapita.columns):
        my_series = list()
        for d in percapita.index.tolist():
            my_series.append([arrow.get(d.year, d.month, d.day).timestamp * 1000, round(percapita.loc[d][country], 1)])

        my_dict = dict()
        my_dict['country'] = country
        my_dict['series'] = my_series
        my_data.append(my_dict)

    print(list(map(
        lambda entry: {'name': entry['country'], 'data': entry['series']},
        my_data)))


    chart = {
        'chart': {
            'type': 'spline',
            'borderColor': '#9DB0AC',
            'borderWidth': 3,
        },
        'title': {'text': 'COVID-19 확진자 발생율'},
        'subtitle': {'text': 'Source: Johns Hopkins University Center for Systems Science and Engineering'},
        'xAxis': {'type': 'datetime',
                  },
        'yAxis': [{
            'labels': {
                'format': '{value} 건/백만 명',
                'style': {'color': 'blue'}
            }, 'title': {
                'text': '합계 건수',
                'style': {'color': 'blue'}
            },
        }, ],
        'plotOptions': {
            'spline': {
                'lineWidth': 3,
                'states': {
                    'hover': {'lineWidth': 5}
                },
            }
        },
        'series': list(map(
            lambda entry: {'name': entry['country'], 'data': entry['series']},
            my_data)
        ),
        'navigation': {
            'menuItemStyle': {'fontSize': '10px'}
        },
    }
    dump = json.dumps(chart)
    return render(request, 'covid19.html', {'chart': dump})



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
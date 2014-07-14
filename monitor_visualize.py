# -*- coding: utf-8 -*-
import sys
import os
import matplotlib.pyplot as plt
import plotly.plotly as py
from plotly.graph_objs import Figure,Data,Layout,XAxis,YAxis,Scatter
from datetime import datetime,timedelta
from StringIO import StringIO
import locale

def convert_measured_date(dates):
  time_type = "minutes"
  if dates:
    date_min = min(dates)
    x = [(date - date_min).total_seconds()/60 for date in dates]
  else:
    x = []

  if x and max(x) > 239:
    x = [e/60 for e in x]
    time_type = "hours"
  return (x, time_type)

def visualize_shares_post(dates,vk,fb,tw, post_id, title):
  locale.setlocale(locale.LC_ALL, 'en_US.utf8')
  api_key      = os.environ.get("PLOTLY_KEY_API")
  py.sign_in('SergeyParamonov', api_key)
  vk_trace = Scatter(
                     x=dates,
                     y=vk,
                     mode='lines+markers',
                     name=u"Вконтакте"
  )
  fb_trace = Scatter(
                     x=dates,
                     y=fb,
                     mode='lines+markers',
                     name=u"Facebook"
  )
  tw_trace = Scatter(
                     x=dates,
                     y=tw,
                     mode='lines+markers',
                     name=u"Twitter"
  )
  data = Data([vk_trace,fb_trace,tw_trace])
  layout = Layout(title=u"Репосты: " + title,
      xaxis= XAxis(title=u"Московское время"), # x-axis title
      yaxis= YAxis(title=u"Репосты"), # y-axis title
      hovermode='closest', # N.B hover -> closest data pt
  )
  plotly_fig = Figure(data=data, layout=layout)
  plotly_filename = "monitor_post_id_" + str(post_id) + "_" + "shares"
  unique_url = py.plot(plotly_fig, filename=plotly_filename)
  return unique_url

def visualize_post(dates,y, field):
  locale.setlocale(locale.LC_ALL, 'en_US.utf8')
  time, time_type = convert_measured_date(dates)
  fig = plt.figure()
  plt.plot(time, y, "-o")
  plt.xlabel(time_type)
  plt.ylabel(field)
  return plt.gcf()

#x -- dates
#y -- views or favorites
#field -- info on y
def visualize_post_plotly(x, y, field, post_id, title):
  api_key      = os.environ.get("PLOTLY_KEY_API")
  py.sign_in('SergeyParamonov', api_key)
  data = Data([Scatter(x=x,y=y)])
  if field == "favorite":
    ytitle = u"Избранное"
  else:
    ytitle = u"Просмотры"
  layout = Layout(title=ytitle+": "+title,
      xaxis= XAxis(title=u"Московское время"), # x-axis title
      yaxis= YAxis(title=ytitle), # y-axis title
      showlegend=False,    # remove legend (info in hover)
      hovermode='closest', # N.B hover -> closest data pt
      )
  plotly_fig = Figure(data=data, layout=layout)
  plotly_filename = "monitor_post_id_" + str(post_id) + "_" + field
  unique_url = py.plot(plotly_fig, filename=plotly_filename)
  return unique_url

def create_monitor_figure(post_id, datatype, monitor_database, title):
  locale.setlocale(locale.LC_ALL, 'en_US.utf8')
  post_id = int(post_id)
  data = monitor_database.find({"post_id":post_id}).sort("overall_seconds",1)
  x = []
  if datatype == "shares":
    vk, fb, tw = [],[],[]
    vk_f, fb_f, tw_f  = "vkontakte_data","facebook_data", "twitter_data"
    for datum in data:
      x.append(datetime(datum["year"], datum["month"], datum["day"], datum["hour"], datum["minute"]))
      vk.append(datum[vk_f]); fb.append(datum[fb_f]); tw.append(datum[tw_f])
    fig_url = visualize_shares_post(x,vk,fb,tw,post_id,title)
  else:
    y = []
    if datatype == "pageview":
      field = "views"
    if datatype == "favorites":
      field = "favorite"
    for datum in data:
      x.append(datetime(datum["year"], datum["month"], datum["day"], datum["hour"], datum["minute"]))
      y.append(datum[field])
    fig_url = visualize_post_plotly(x,y,field, post_id, title)
  return fig_url

def process_data_for_pulse(data):
  xy = []
  for datum in data:
    date_dif = datum['date1'] - datum['date2']
    num_of_minutes = date_dif.seconds/60
    y = datum['dif'] / num_of_minutes
    d = datum['date1']
    x = d+timedelta(hours=4) # +4 to adjust to moscow time
    xy.append((x,y))
  sorted_tuples = sorted(xy)
  x = [e[0] for e in sorted_tuples]
  y = [e[1] for e in sorted_tuples]
  return (x,y)

def create_pulse_figure(data):
  locale.setlocale(locale.LC_ALL, 'en_US.utf8')
  x, y = process_data_for_pulse(data)
  fig = plt.figure()
  plt.xlabel("Moscow Time Zone +4 UTC")
  plt.ylabel("Difference in views")
  plt.plot(x, y, "-o")
  fig.set_size_inches(18.5,10.5)
  return fig

def plotly_create_stream(data):
  api_key      = os.environ.get("PLOTLY_KEY_API")
  stream_token = os.environ.get("PULSE_STREAM_TOKEN")
  x, y = process_data_for_pulse(data)
  py.sign_in('SergeyParamonov', api_key)
  data = Data([Scatter(x=x,y=y,stream=dict(token=stream_token))])
  layout = Layout(title="Пульс Хабра — изменение просмотров статей в Новом (в минуту)",
      xaxis= XAxis(title=u"Московское время"), # x-axis title
      yaxis= YAxis(title=u"Просмотры"), # y-axis title
      showlegend=False,    # remove legend (info in hover)
      hovermode='closest', # N.B hover -> closest data pt
      )
  plotly_fig = Figure(data=data, layout=layout)
  unique_url = py.plot(plotly_fig, filename="pulse")
  return unique_url



# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from dateutil.parser import parse
from datetime import datetime
from utils import debug


def compress_large_array(dates):
  if len(dates) <= 60:
    return dates
  else:
    years = []
    for date in dates:
      year     = date.year
      years.append(year)
    year = years[0]
    dates = []
    dates.append(year)
    for i in range(1,len(years)):
      if years[i] == year:
        dates.append("")
      else:
        year = years[i]
        dates.append(year)
    return dates

def omit_current_year(date):
  if date.year != datetime.now().year:
    return date.strftime('%d %b %y') 
  return date.strftime('%d %b') 

def visualize_y(x,y):
  x = compress_large_array(x)
  x = map(omit_current_year, x)
  fig, ax = plt.subplots()
  plt.plot(y, '-o')
  x_range = range(len(y))
  plt.xticks(x_range,x,rotation=70,fontsize=9)
  plt.axis('on') 
   # recompute the ax.dataLim
  ax.relim()
  # update ax.viewLim using the new dataLim
  ax.autoscale_view()
  plt.subplots_adjust(bottom=0.15)
  return fig

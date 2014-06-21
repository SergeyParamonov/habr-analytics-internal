# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from dateutil.parser import parse

rus_to_eng = {u"января":"Jan", u"февраля":"Feb", u"марта":"Mar", u"апреля":"Apr", u"мая":"May", u"июня":"June", u"июля":"July", u"августа":"Aug",u"сентября":"Sep", u"октября":"Oct", u"ноября":"Nov", u"декабря":"Dec"}

def compress_large_array(dates):
  if len(dates) <= 60:
    return dates
  else:
    years = []
    for date in dates:
      try:
        date_obj = parse(date)
      except:
        data_obj = parse("")
      year     = date_obj.year
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
    

def change_dates(dates):
  dates = [date.replace(u" в "," ")[:-6] for date in dates]
  newDates = []
  for date in dates:
    isSubstituted = False
    for k, v in rus_to_eng.items():
      if date != date.replace(k,v):
        isSubstituted = True
        newDate = date.replace(k,v)
    if isSubstituted:
      newDates.append(newDate)
    else:
      newDates.append(date)
  return compress_large_array(newDates)
        

def visualize_y(x,y):
  x = change_dates(x)
  plt.figure()
  plt.plot(y, '-o')
  x_range = range(len(y))
  ax      = plt.subplot(111)
  plt.xticks(x_range, x,rotation=80,  fontsize=9)
  plt.axis('on') 
  ax = plt.gca()
   # recompute the ax.dataLim
  ax.relim()
  # update ax.viewLim using the new dataLim
  ax.autoscale_view()
  plt.subplots_adjust(bottom=0.15)
  return plt.gcf()

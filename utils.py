# -*- coding: utf-8 -*
from __future__ import print_function
from flask import Markup
import matplotlib.pyplot as plt
import os.path
import os
import sys
from datetime import datetime, date, timedelta
import pymongo
import time
from dateutil.parser import parse
import pytz
import calendar
from base64 import b64encode, b64decode
from monitor_visualize import create_pulse_figure
from StringIO import StringIO


rus_to_eng = {u"января":"Jan", u"февраля":"Feb", u"марта":"Mar", u"апреля":"Apr", u"мая":"May", u"июня":"June", u"июля":"July", u"августа":"Aug",u"сентября":"Sep", u"октября":"Oct", u"ноября":"Nov", u"декабря":"Dec"}

def get_data_from_column(data, column_index):
  output = []
  for line in data:
    tmp = line.decode('utf8')
    output.append(tmp.split(',')[column_index-1].strip())
  return output

def validate_hubs(hub_list, hub_names):
  error, hub1, hub2, hub3 = None, None, None, None
  if hub_list:
    error_text = ""
    hub_list = filter(lambda x: x != "", hub_list)
    #check that 2 or 3 hubs are given
    if len(hub_list) < 2 or len(hub_list) > 3:
      error_text = u'\u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u0434\u0432\u0430 \u0438\u043b\u0438 \u0442\u0440\u0438 \u0445\u0430\u0431\u0430. '
    #check that hubs actually exist
    wrong_hub_name = False
    for hub in hub_list:
      if hub not in hub_names:
        wrong_hub_name = True 
    if wrong_hub_name:
      error_text = error_text + u'\u041d\u0435\u0432\u0435\u0440\u043d\u043e\u0435 \u0438\u043c\u044f \u0445\u0430\u0431\u0430.'
    if error_text:   
      error = Markup('<div class="row"> <div style="font-size:20px;" class="col-md-4 col-md-offset-4 alert alert-danger">'+error_text+'</div></div>')
    if not error:
      hub1 = hub_list[0]
      hub2 = hub_list[1]
      if len(hub_list) == 3:
        hub3 = hub_list[2]
  return (error,hub1,hub2,hub3)

def validate_hubs_hist(hub, hub_names):
  error, error_text = None, None
  if hub and hub not in hub_names: 
    error_text = u'Указан неверный хаб'
  if error_text:
    error = Markup('<div class="row"> <div style="font-size:20px;" class="col-md-4 col-md-offset-4 alert alert-danger">'+error_text+'</div></div>')
  return (error,hub)


#def post_head():
#  return "year, month, day, hour, minute, post_id, views, favorite, twitter_data, facebook_data, vkontakte_data\n"

def write_post_data(data,timestamp,monitor):
  try:
    post_id, title, views, favorite, twitter_data, facebook_data, vkontakte_data = data 
    year, month, day, hour, minute                                        = timestamp 
  except:
   #habr_analytics_log(str(post_id))
    return None
  date = datetime(year, month, day, hour, minute)
  overall_seconds = calendar.timegm(date.timetuple())
  monitor.insert({"post_id":post_id, "views":views, "favorite":favorite, "twitter_data":twitter_data, "facebook_data":facebook_data, "vkontakte_data":vkontakte_data, "year":year, "month":month, "day":day, "hour":hour, "minute":minute, "overall_seconds":overall_seconds})
 #path = "data/posts/"+str(post_id)
 #if not os.path.isfile(path):
 #  first_write = True
 #else:
 #  first_write = False
 #post_file = open(path,"a+")
 #if first_write:
 #  post_file.write(post_head())
 #record = str(year)+","+ str(month)+","+ str(day) +","+ str(hour)+","+ str(minute)+","+ str(post_id)+","+ str(views)+","+ str(favorite)+","+ str(twitter_data)+","+ str(facebook_data)+","+ str(vkontakte_data)+"\n"
 #post_file.write(record)


def convert_date(date_str):
#    app.logger.debug(date_str)
 #try:
    date_str = date_str.replace(u" в ",u" ")
    today_str = u"сегодня"
    yesterday_str = u"вчера"
    if   today_str     in date_str: 
      rowDate = date_str.replace(today_str,"")
      date = parse(rowDate)
      return date
    elif yesterday_str in date_str:
      rowDate = date_str.replace(yesterday_str,"")
      date = parse(rowDate) - timedelta(days=1)
      return date
    else: #replace cyrillics in date and parse
#     app.logger.debug("passed")
      for k, v in rus_to_eng.items():
        if date_str != date_str.replace(k,v):
          rowDate = date_str.replace(k,v)
          date = parse(rowDate)
          return date
      print("something is wrong with date")
      return datetime.now(pytz.utc) 
 #except Exception as e:
#   app.logger.debug(str(e))
    return datetime.now(pytz.utc)

def delete_post(post_id, key, collection):
  collection.remove({key:post_id})
 #all_posts = monitor.find({})
 #path = "data/posts/"+str(post_id)
 #try:
 #  os.remove(path)
 #  habr_analytics_log(str(post_id))
 #except Exception as e:
 #  habr_analytics_log(e)

def clean_old(dict_dates, monitor, id_title, monitor_datatypes, cache):
  now = datetime.now()
  two_days = timedelta(days = 2)
# one_day = timedelta(seconds = 0)
  for k,v in dict_dates.items():
    if now - v > two_days:
      del dict_dates[k]
      delete_post(k,"post_id", monitor)
      delete_post(k,"_id",id_title)
      for datatype in monitor_datatypes.keys():
        cache.delete(make_fig_key(k,datatype))

def update_posts(dict_values,timestamp,monitor_database):
  for k,v in dict_values.iteritems():
    write_post_data(v,timestamp,monitor_database)

def habr_analytics_log(message):
   log = open("app_log.txt", "a")
   log.write(str(message))
   log.close()

def make_fig_key(post_id, datatype):
  key = str(post_id) + ":" + str(datatype)
  return key

def convert_user_datatype_to_figure_types(datatype):
  datatypes_conversion =  {"pageview":"views", "favorites":"favorite", "score":"score"}
  return datatypes_conversion[datatype]

def compute_dif(new, old):
  dif = 0
  if new:
    date1 = new[0]['timestamp']
  else:
    date1 = None
  if old:
    date2 = old[0]['timestamp']
  else:
    date2 = None
  # if new data is not "fresh", then get out of here
  if not (date1 > date2) or not date1 or not date2:
    return None
  for post1 in new:
    id1 = post1['_id']
    for post2 in old:
      id2 = post2['_id']
      if id1 == id2:
        dif += post1['views'] - post2["views"]
  return {"dif":dif, "date1":date1, "date2":date2}
 
def debug(debug_string):
  print(str(debug_string))
  sys.stdout.flush() 

def get_records_by_time(pulse_stats):
  data = list(pulse_stats.find({}).sort("date1",-1))
  data.reverse()
  data = data[:205]
  return data

def clean_update_and_create_figure(new, old, pulse_stats, pulse_figure_db):
  dif = compute_dif(new,old)
  if dif:
    pulse_stats.insert(dif)
  data = get_records_by_time(pulse_stats)
  pulse_stats.remove({})
  pulse_stats.insert(data)
  fig  = create_pulse_figure(data)
  img  = StringIO()
  fig.savefig(img)
  img.seek(0)
  plt.close(fig)
  str_img = b64encode(img.read())
  timestamp = datetime.now()
  pulse_figure_db.remove({})
  pulzase_figure_db.insert({"figure_binary":str_img, "timestamp":timestamp})

def get_pulse_figure(pulse_figure_db):
  encoded_figure = pulse_figure_db.find_one({})['figure_binary']
  decoded_figure = b64decode(encoded_figure)
  img            = StringIO(decoded_figure)
  img.seek(0)
  return img

# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import urllib3
from bs4 import BeautifulSoup
import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
from datetime import datetime 
from flask import flash
import json
import sys
sys.path.append("src/")
from utils import convert_date
# dependencies of monitor_call
from utils import make_fig_key, clean_old, update_posts
from monitor_visualize import create_monitor_figure
from user_visualize import visualize_y
from dateutil.parser import parse
from StringIO import StringIO
from bson import Binary
from base64 import b64encode 
import pytz



def extract_data(html):
  score_is_not_shown = u'—'
  #id 
  post_id  = int(html['id'][5:])
  #рейтинг
  scoreRow = html.find(class_="score")
  if scoreRow and scoreRow.text != score_is_not_shown:
    try:
      score = int(scoreRow.text)
    except:
      score = -1*int(scoreRow.text[1:])
  else:
    score = None
  #избранное
  try:
    views = int(html.find(class_="pageviews").text)
  except:
#   print(html)
    print("ERROR PAGEVIEWS")
    views = None
  #просмотры
  try:
    favorite = html.find(class_="favs_count").text
    if favorite.isdigit():
      favorite = int(favorite)
    else:
      favorite = 0
  except:
    favorite = None
    print(html)
    print("ERROR FAV")
  date = html.find(class_="published").text
  return {"post_id":post_id, "score":score, "views":views, "favorite":favorite, "date":date}

def get_topics_data(username):
  MAX_PAGES = 250
  http = urllib3.PoolManager()
  url  = "http://habrahabr.ru/users/"+username+"/topics/page"
  divclass = "post"
  data     = []
  i  = 1
  while i <= MAX_PAGES:
    try:
      # url + str(i) iterates over pages of topics created by the user
      page_url = url+str(i)
      print(page_url)
      response = http.request('GET', page_url, headers={"cache-control": "no-cache"})
    except urllib3.exceptions.HTTPError as err:
      if err.code == 404:
        break
      else:
        break
    html     = response.data.decode("utf-8")
    soup     = BeautifulSoup(html)
    articles = soup.find_all(class_=divclass)
    if articles:
      for article in articles:
        data.append(extract_data(article))
      i += 1   
    else:
      break
  data.reverse()
  return data

def get_dates(data):
  dates = [datum['date'] for datum in data]
  return dates

def get_fav(data):
  return [datum['favorite'] for datum in data]

def get_views(data):
  return [datum['views'] for datum in data]

def get_scores(data):
  return [datum['score'] for datum in data]


def get_top_users():
  url = 'http://habrahabr.ru/users/'
  http = urllib3.PoolManager()
  user_class = "username"
  tm_users = ['boomburum', 'alizar', 'ilya42', 'deniskin']
  try:
    response = http.request('GET', url, headers={"cache-control": "no-cache"})
  except: 
    print("error")
    return []
  html  = response.data.decode("utf-8")
  soup  = BeautifulSoup(html)
  usersRow = soup.find_all(class_=user_class)
  users = [user.text.lower() for user in usersRow]  
  return users + tm_users

def update_topusers(topusers_database):
  users = get_top_users()
  topusers_database.remove({})
  timestamp = datetime.now()
  for user in users:
    data = get_topics_data(user)
    for data_selector, descr in [(get_views,"views"), (get_fav,"favorite"), (get_scores,"score")]:
      y_values = data_selector(data)
      dates = get_dates(data)
      fig   = visualize_y(dates,y_values)
      img   = StringIO()
      fig.savefig(img)
      img.seek(0)
      plt.close(fig)
      str_img = b64encode(img.read())
      topusers_database.insert({"user": user, "datatype": descr, "figure_binary":str_img, "timestamp":timestamp, "type":"monitor"})

def update_date_dictionary(dates_dict):
  url = "http://habrahabr.ru/posts/collective/new/page"
  http = urllib3.PoolManager()
  divclass = "post"
  data     = []
  cut_post_prefix = len("post_")
  i  = 1
  while True:
    try:
      # url + str(i) iterates over pages of topics created by the user
      page_url = url+str(i)
      print(page_url)
      response = http.request('GET', page_url, headers={"cache-control": "no-cache"} )
    except urllib3.exceptions.HTTPError as err:
      if err.code == 404:
        break
      else:
        break
    html     = response.data.decode("utf-8")
    soup     = BeautifulSoup(html)
    articles = soup.find_all(class_=divclass)
    if articles:
      for article in articles:
        try:
          article_id = int(article['id'][cut_post_prefix:])
          rowDate    = article.find(class_="published").text
          date       = convert_date(rowDate)
          dates_dict[article_id] = date
        except Exception as e:
          print(str(e))
          return data
        data.append(article_id)
      i += 1   
    else:
      break
  return data

def init_dates_dict(id_title_database):
  dates = {}
  ids = id_title_database.find({})
  for post_id in ids:
    if post_id['date'] == u"None":
      id_title_database.remove({"_id":post_id['_id']})
    else:
      dates[post_id['_id']] = post_id['date']
  return dates    

#remove all records that in monitor_database (by post_id) but no it_title_database
def clean_old_monitor_records(monitor_database, id_title_database):
  title_records = id_title_database.find({})
  ids_title = [record['_id'] for record in title_records]
  monitor_records = monitor_database.find({})
  ids_monitor = [record['post_id'] for record in monitor_records]
  for post_id in ids_monitor:
    if post_id not in ids_title:
      monitor_database.remove({"post_id":post_id})

def extract_post_all_info(post_id):
  post_id   =  str(post_id)
  twitter   = "https://cdn.api.twitter.com/1/urls/count.json?url=habrahabr.ru/post/"+post_id+"/"
  facebook  = "http://graph.facebook.com/?id=http://habrahabr.ru/post/" + post_id + "/"
  vkontakte = "http://vk.com/share.php?act=count&index=1&url=http://habrahabr.ru/post/" + post_id +"/"
  http = urllib3.PoolManager()
  post_url = "http://habrahabr.ru/post/"+post_id
  try:
    # social counter
    response = http.request('GET', twitter, headers={"cache-control": "no-cache"})
    twitter_data = json.loads(response.data)['count']
  except:
    twitter_data = 0
  try:
    response = http.request('GET', facebook, headers={"cache-control": "no-cache"})
    facebook_data = json.loads(response.data)['shares']
  except:
    facebook_data = 0
  try:
    response = http.request('GET', vkontakte, headers={"cache-control": "no-cache"})
    vkontakte_data = int(response.data[len("VK.Share.count(1,"):-2].strip())
    # parse the post
  except:
    vkontakte_data = 0

  try:
    response = http.request('GET', post_url, headers={"cache-control": "no-cache"})
    html     = response.data.decode("utf-8") 
    soup     = BeautifulSoup(html)
    title    = soup.find(class_="post_title").text
    article = soup.find(class_="post")
    views = int(article.find(class_="pageviews").text)
    favorite = article.find(class_="favs_count").text
    if favorite.isdigit():
      favorite = int(favorite)
    else:
      favorite = 0
  except Exception as e:
    return None

  return (int(post_id), title ,views, favorite, twitter_data, facebook_data, vkontakte_data)


def get_title(post_id):
  post_id   =  str(post_id)
  http = urllib3.PoolManager()
  post_url = "http://habrahabr.ru/post/"+post_id
  try:
    response = http.request('GET', post_url, headers={"cache-control": "no-cache"})
    html     = response.data.decode("utf-8") 
    soup     = BeautifulSoup(html)
    title    = soup.find(class_="post_title").text
    return title
  except:
    return ""

#*modifies* dict_id_title *using* id_title_database
def create_dict_id_title(dict_id_title,id_title_database):
  data = id_title_database.find({})
  dict_id_title.clear()
  for datum in data:
    dict_id_title[datum['_id']] = datum['title']

#REQUIRES LIBRARIES datetime (datetime constructor), pytz, 
#DEPENDS ON SRC/ *monitor_visualize.py*: create_monitor_figure, *utils.py*: make_fig_key, clean_old, update_posts, *network.py* update_date_dictionary, create_dict_id_title, extract_post_all_info
#MODIFIES dict_dates, dict_last_values, dict_id_title,  id_title_database, PoolManager (close connections), cache, monitor_database, pulse_database
def monitor_call(dict_dates, dict_id_title, monitor_database, id_title_database, cache,monitor_datatypes, pulse_database1,pulse_database2):
  # remove the posts older than 2 days
  clean_old(dict_dates, monitor_database, id_title_database, monitor_datatypes, cache)
  # remove all old records from monitor database, this might happen due to errors or restarts of the server
  clean_old_monitor_records(monitor_database, id_title_database)
  # create timestamp with current time
  now = datetime.now(pytz.utc)
  timestamp = (now.year, now.month, now.day, now.hour, now.minute)
  # mark all posts with the current timestamp
  update_date_dictionary(dict_dates)
  # drop all last values
  dict_last_values = {}
  # iterate over all "fresh" posts and get the data
  pulse_database1.remove({})
  old = pulse_database2.find({})
  pulse_database1.insert(list(old))
  pulse_database2.remove({})
  for post_id,date in dict_dates.iteritems():
    datum = extract_post_all_info(post_id)
    if datum:
      dict_last_values[post_id] = datum 
      pulse_database2.insert({"_id":post_id, "views": datum[2], "timestamp": list(timestamp)})
      # keep track of the titles in the id_title_database to display it for user in the form monitorform
      id_title_database.insert({"_id":post_id, "title": datum[1], "date": date})
  # actually update the monitor database with new data
  update_posts(dict_last_values,timestamp,monitor_database)
  # update available titles and their id-s in the app *dict_id_title* by getting data from *id_title_database*
  create_dict_id_title(dict_id_title,id_title_database)
  # close all connection to actually get "fresh" data from habrahabr
  pool_manager = urllib3.PoolManager()
  pool_manager.clear()
  # cache all the images with new data
  for post_id in dict_dates.keys():
    for datatype in monitor_datatypes.keys():
      img = create_monitor_figure(post_id, datatype, monitor_database)
      cache.set(make_fig_key(post_id,datatype),img)

def get_date_by_id(post_id):
  url = "http://habrahabr.ru/post/" + str(post_id)
  http = urllib3.PoolManager()
  try:
    response = http.request('GET', url, headers={"cache-control": "no-cache"} )
    html     = response.data.decode("utf-8")
    soup     = BeautifulSoup(html)
    rowDate  = soup.find(class_="published").text
    date     = convert_date(rowDate)
  except:
    print("ERROR: Could not get the date, post_id: " + str(post_id))
    return None
  return date

def close_connections():
  http = urllib3.PoolManager()
  http.clear()

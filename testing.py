# -*- coding: utf-8 -*-
import os
import sys
sys.path.append("src/")
from network import *
from user_visualize import visualize_y
import urlparse
from monitor_visualize import *
from utils import debug
from dateutil.parser import parse
import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')
# dict_dates = {}
# dict_last_values = {}
# id_list = get_id_new_posts(dict_dates)
# for id_post in id_list:
#   dict_last_values[id_post] = extract_post_all_info(id_post)

#import pymongo
#MONGO_URL = os.environ.get('MONGOHQ_URL')
print(update_date_dictionary({}))


# Get a connection
#conn = pymongo.Connection(MONGO_URL)
# Get the database
#db = conn[urlparse.urlparse(MONGO_URL).path[1:]]
#monitor_plotly_url = db.monitor_plotly_url
#monitor_plotly_url.remove({})
#data = get_records_by_time(db.pulse_stats)
#plotly_create_stream(data)
#topusers_database = db.topusers
#create_pulse_figure(pulse_stats.find({}))
#plt.show()
#cached_users = db.cached_users
#update_topusers(cached_users)
#data = get_topics_data("lozga")
#for data_selector, descr in [(get_views,"views"), (get_fav,"favorite"), (get_scores,"score")]:
#  y_values = data_selector(data)
#  dates = get_dates(data)
#  fig   = visualize_y(dates,y_values)

#plt.show()

#data = pulse_stats.find({})
#def convert_to_date(d):
#  return datetime(d[0],d[1],d[2],d[3],d[4])
#pulse_stats.remove({})
#for datum in data:
#  pulse_stats.insert({'dif':datum['dif'], 'date1':convert_to_date(datum['date1']), 'date2':convert_to_date(datum['date2'])})

#print(convert_date(u"1 июля в 11:17"))
#monitor_database = db.monitor
#id_title_database = db.id_title
#cached_users = db.cached_users


#monitor_database = db.monitor
#id_title_database = db.id_title


#for post_id in ids:
# if post_id['date'] is None:
#   id_title.remove({"_id":post_id['_id']})
#create_monitor_figure(226353,"pageview",posts)

#data = fetch_data_from_mongo("alizar", db.topusers)
#for datum in data:
#  print(datum['post_id'], datum['date'])
#id_title.remove({})
#posts.remove({})
#update_topusers(topusers_db)
#post = id_title.find({"id_post": 226217})
#dict_dates_tmp=init_dates_dict(posts)
#for post_id,date in dict_dates_tmp.iteritems():
#  print(post_id)
#  id_title.insert({"post_id":post_id,"title":get_title(post_id)})
#print(extract_post_all_info(222123))
#topusers_database = db.topusers
#users = update_topusers(topusers_database)
#data =fetch_data_from_mongo("valdikss", topusers_database)
#for datum in data:
#  print datum['views']

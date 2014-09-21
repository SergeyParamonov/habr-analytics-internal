# -*- coding: utf-8 -*-

import os
import sys
sys.path.append("src/")
from network import get_topics_data, get_fav, get_views, get_scores, get_dates, get_top_users, update_topusers, extract_post_all_info, fetch_data_from_mongo, init_dates_dict, get_title, fetch_data_from_mongo, get_date_by_id, clean_old_monitor_records
from user_visualize import visualize_y
import urlparse
from monitor_visualize import create_monitor_figure
from utils import convert_date 
from dateutil.parser import parse

# dict_dates = {}
# dict_last_values = {}
# id_list = get_id_new_posts(dict_dates)
# for id_post in id_list:
#   dict_last_values[id_post] = extract_post_all_info(id_post)

import pymongo
MONGO_URL = os.environ.get('MONGOHQ_URL')


# Get a connection
conn = pymongo.Connection(MONGO_URL)
# Get the database
db = conn[urlparse.urlparse(MONGO_URL).path[1:]]
topusers_database = db.topusers

monitor_database = db.monitor
id_title_database = db.id_title


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

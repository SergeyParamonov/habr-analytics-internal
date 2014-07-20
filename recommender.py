# -*- coding: utf-8 -*-
from __future__ import print_function
from bs4 import BeautifulSoup
import urllib3
import locale
import sys
sys.path.append("src/")
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from datetime import datetime
import re
import csv
#my functions
from network import get_title
from draw import jaccard_index

def extract_recommender_info(article):
  rowData = article.find(class_="post_title")['href']
  matched = re.search(r"\d\d\d\d+", rowData)
  if not matched:
    return None
  post_id = matched.group(0)
  return int(post_id)

def get_fav_by_username(username):
  http = urllib3.PoolManager()
  url  = "http://habrahabr.ru/users/"+username+"/favorites/page"
  MAX_PAGES = 250
  divclass = "post"
  i  = 1
  post_ids = []
  while i <= MAX_PAGES:
    try:
      page_url = url+str(i)
      response = http.request('GET', page_url, headers={"cache-control": "no-cache"})
    except urllib3.exceptions.HTTPError as err:
      print("ERROR: "+page_url)
      return None
    html     = response.data.decode("utf-8")
    soup     = BeautifulSoup(html)
    articles = soup.find_all(class_=divclass)
    if articles:
      for article in articles:
        post_id = extract_recommender_info(article)
        if post_id:
          post_ids.append(post_id)
      i += 1   
    else:
      break
  return post_ids

def extract_author_commenters(post_id):
  usernames = set()
  http = urllib3.PoolManager()
  url = "http://habrahabr.ru/post/" + str(post_id)
  try:
    response = http.request('GET', url, headers={"cache-control": "no-cache"})
    html         = response.data.decode("utf-8")
    soup         = BeautifulSoup(html)
    author       = str(soup.find(class_= "author").a.text)
    usernames.add(author)
    commentators = soup.find_all(class_= "username")
    for user in commentators:
      usernames.add(str(user.text))
    return usernames
  except:
    return set()

def get_all_user_names():
  # first posts from 2013
  log           = open("username_log.txt", "w")
  first_post_id = 165001
  last_post_id  = 223000
  users         = set()
  for post_id in xrange(first_post_id, last_post_id):
    print(post_id, end="", file=log)
    newUsers = extract_author_commenters(post_id)
    if newUsers:
      print(" OK", file=log)
      users_file = open("users_file.txt","w")
      users |= newUsers
      users_file.write(str(users))
      users_file.close()
    else:
      print(" Empty", file=log)
    log.flush()  
  log.close()   

def get_all_users_fav():  
  fav_filename = "data/recommender/user_fav.csv"
  empty_users_file = open("empty_users.txt", "a+")
  empty_users = empty_users_file.read().splitlines()
  users = eval(open("data/recommender/user_list.txt").read())
  user_fav_csv = open(fav_filename,"a+")
  downloaded_users = read_all_usernames(fav_filename)
  for user in users:
    if user not in downloaded_users and user not in empty_users:
      print("Processing: " +user)
      favs = get_fav_by_username(user)
      if favs:
        print(user + " OK")
        print(user + ',' + ' '.join([str(e) for e in favs]),file=user_fav_csv)
        user_fav_csv.flush()
      else:
        print(user+" EMPTY")
        print(user, file=empty_users_file)
        empty_users_file.flush()
  user_fav_csv.close()    
  empty_users_file.close()

def read_all_usernames(filename):
  usernames = []
  data = open(filename).readlines()
  for line in data:
    username, post_ids = line.split(',')
    usernames.append(username)
  return usernames

def read_preferences():
  filename = "./data/recommender/user_favorites.csv"
  data = open(filename).read().splitlines()
  header = True
  preferences = {}
  for line in data:
    if header: #ignore header of the columns 
      header = False
      continue
    username, str_post_ids = line.split(',')
    post_ids = [int(e) for e in str_post_ids.split(' ')]
    preferences[username] = set(post_ids)
  return preferences

def read_weigths():
  count_file   = open("./data/recommender/post_counts.csv", "r")
  count_reader = csv.reader(count_file)
  counts = {}
  i = 0
  for row in count_reader:
    counts[int(row[0])] = int(row[1])
  return counts

def get_all_posts(preferences):
  all_posts    = set()
  counts       = []
  count_file   = open("./data/recommender/post_counts.csv", "w")
  for user, pref in preferences.iteritems():
    all_posts |= pref 
  return all_posts

def compute_weigths(preferences):
  preferences = read_preferences()
  all_posts   = get_all_posts(preferences)
  count_file   = open("./data/recommender/post_counts.csv", "w")
  count_writer = csv.writer(count_file)
  for post in all_posts:
    print(post)
    count = 0
    for user, pref in preferences.iteritems():
      if post in pref:
        count += 1 
    count_writer.writerow([post, count])
    count_file.flush()
  count_file.close()

def transform_all_csv():
  file_in  = open("data/recommender/all.csv","r")
  csv_reader   = csv.reader(file_in)
  file_out= open("data/recommender/titles.csv","w")
  csv_writer = csv.writer(file_out)
  for row in csv_reader:
    csv_writer.writerow([row[0], row[1]])
  file_in.close()
  file_out.close()

def read_titles():
  titles = {}
  title_file = open("data/recommender/titles.csv", "r")
  title_reader = csv.reader(title_file)
  for row in title_reader:
    titles[int(row[0])] = row[1]
  return titles

def download_new_titles(preferences):
  preferences = read_preferences()
  all_posts   = get_all_posts(preferences)
  file_out= open("data/recommender/titles.csv","a")
  csv_writer = csv.writer(file_out)
  for post in all_posts:
    if post > 218345:
      title = get_title(post).encode("utf-8")
      csv_writer.writerow([post,title])
      file_out.flush()
  file_out.close()

def get_titles(ids, titles):
 answer = []
 for post_id in ids:
   if post_id in titles:
     answer.append((post_id, titles[post_id]))
   else:
     answer.append((post_id, get_title(post_id)))
 return answer

def generate_link_by_id(post_id):
  return "http://habrahabr.ru/post/" + str(post_id)

def get_top_N_similar(username, preferences, N):
  user_preference = preferences[username]
  similar = [(jaccard_index(user_preference, preference), other_user) for other_user, preference in preferences.iteritems() if other_user != username]
  similar.sort(reverse=True)
  return similar[:N]

def occurs_in(post_id, preferences, users):
  count = 0
  for user in users:
    preference = preferences[user]
    if post_id in preference:
      count += 1
  return count

#uncomment to make give_recommendations work!
def give_recommendations(username, preferences, titles):
  N             = 15 # neigbourhood of the input-user
  preference    = preferences[username] # set of favourite posts for input-user
  top_similar   = get_top_N_similar(username, preferences, N) #top similar users + their similarity
  similar_users = [user for similarity, user in top_similar]  #only similar usernames
  rank          = {}
  for similarity, other_user in top_similar:
    other_preferences = preferences[other_user] 
    for post_id in other_preferences:
      if post_id not in preference:
        rank.setdefault(post_id,0)
        rank[post_id] += similarity
  recommendations = [(similarity/occurs_in(post_id, preferences, similar_users), post_id) for post_id, similarity in rank.iteritems()]
  recommendations.sort(reverse=True)
  M = 20 # overall number of recommendations
  WITH_TITLE = 3 # articles with titles
  recommendation_topM = recommendations[:M]
  recommendation_ids  = [post_id for similarity, post_id in recommendation_topM]
  first_answer = get_titles(recommendation_ids[:WITH_TITLE], titles)
  other_answer = recommendation_ids[WITH_TITLE:M]
  return (first_answer,other_answer)

# -*- coding: utf-8 -*-
from __future__ import print_function
from bs4 import BeautifulSoup
import urllib3
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from datetime import datetime
import re

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
  fav_filename = "user_fav.csv"
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

get_all_users_fav()

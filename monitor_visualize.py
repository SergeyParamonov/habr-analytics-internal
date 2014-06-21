import matplotlib.pyplot as plt
from datetime import datetime
from StringIO import StringIO

def convert_measured_date(dates):
  time_type = "minutes"
  date_min = min(dates)
  
  x = [(date - date_min).total_seconds()/60 for date in dates]
  if max(x) > 239:
    x = [e/60 for e in x]
    time_type = "hours"
  return (x, time_type)

def visualize_shares_post(dates,vk,fb,tw):
  time, time_type = convert_measured_date(dates)
  fig = plt.figure()
  ax  = plt.gca()
# plt.xticks(minutes,dates,rotation=80,  fontsize=9)
  plt.plot(time, vk, "-o", label="vkontakte"); plt.plot(time, fb, "-o", label="facebook"); plt.plot(time, tw, "-o",label="twitter")
  plt.xlabel(time_type)
  plt.ylabel("shares")
  max_share = max(max(vk), max(fb), max(tw))
  ax.set_ylim(0,max_share+1)
  plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10), ncol=3, fancybox=True, shadow=True)
  return plt.gcf()

def visualize_post(dates,y, field):
  time, time_type = convert_measured_date(dates)
  fig = plt.figure()
  plt.plot(time, y, "-o")
  plt.xlabel(time_type)
  plt.ylabel(field)
  return plt.gcf()

def create_monitor_figure(post_id, datatype, monitor_database):
  post_id = int(post_id)
  data = monitor_database.find({"post_id":post_id}).sort("overall_seconds",1)
  x = []
  if datatype == "shares":
    vk, fb, tw = [],[],[]
    vk_f, fb_f, tw_f  = "vkontakte_data","facebook_data", "twitter_data"
    for datum in data:
      x.append(datetime(datum["year"], datum["month"], datum["day"], datum["hour"], datum["minute"]))
      vk.append(datum[vk_f]); fb.append(datum[fb_f]); tw.append(datum[tw_f])
    fig = visualize_shares_post(x,vk,fb,tw)
  else:
    y = []
    if datatype == "pageview":
      field = "views"
    if datatype == "favorites":
      field = "favorite"
    for datum in data:
      x.append(datetime(datum["year"], datum["month"], datum["day"], datum["hour"], datum["minute"]))
      y.append(datum[field])
    fig = visualize_post(x,y,field)
  img  = StringIO()
  fig.savefig(img)
  img.seek(0)
  plt.close(fig)
  return img

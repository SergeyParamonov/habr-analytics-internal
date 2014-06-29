import matplotlib.pyplot as plt
from datetime import datetime,timedelta
from StringIO import StringIO

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

def visualize_shares_post(dates,vk,fb,tw):
  time, time_type = convert_measured_date(dates)
  fig = plt.figure()
  ax  = plt.gca()
# plt.xticks(minutes,dates,rotation=80,  fontsize=9)
  plt.plot(time, vk, "-o", label="vkontakte"); plt.plot(time, fb, "-o", label="facebook"); plt.plot(time, tw, "-o",label="twitter")
  plt.xlabel(time_type)
  plt.ylabel("shares")

  max_vk = max(vk) if vk else 0
  max_fb = max(fb) if fb else 0
  max_tw = max(tw) if tw else 0
  max_share = max(max_vk, max_fb, max_tw)
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

def create_pulse_figure(data):
  xy = []
  for datum in data:
    y = datum['dif']
    d = datum['date1']
    x = datetime(d[0],d[1],d[2],d[3],d[4])+timedelta(hours=2) # +2 to adjust to moscow time
    xy.append(x,y)
  sorted_tuples = sorted(xy)
  x = [e[0] for e in sorted_tuples]
  y = [e[1] for e in sorted_tuples]
  fig = plt.figure()
  plt.xlabel("Moscow Time Zone +4 UTC")
  plt.ylabel("Difference in views")
  plt.plot(x, y, "-o")
  fig.set_size_inches(18.5,10.5)
  return fig

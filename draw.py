#!/usr/bin/env python 
import glob
import operator
import pylab as pl
from matplotlib_venn import venn2, venn3
import matplotlib.pyplot as plt
from matplotlib.pyplot import gca

def percent_of(set1,set2):
  dif = set1 & set2
  return str(int(100*len(dif)/len(set1)))

def read_list_of_users(hubname):
    filename  = "data/hubs/" + hubname
    user_file = open(filename, "r")
    users     = user_file.readlines()
    users     = [user.strip() for user in users]
    return users

def draw(set1, set2, set3, label1, label2, label3):
  plt.figure()
  set1 = set(set1)
  set2 = set(set2)
  if label3:
    set3 = set(set3)
    v = venn3([set1,set2, set3], (label1, label2, label3))
    plt.title('Venn diagram for hubs: ' + label1 + "," + label2 +"," + label3, fontsize=20)
  else:
    v = venn2([set1, set2], (label1, label2))
    plt.title('Venn diagram for hubs:' + label1 + "," + label2, fontsize=20)
  if v.get_patch_by_id('100'):
    v.get_patch_by_id('100').set_color("blue")
  if v.get_patch_by_id('010'):
    v.get_patch_by_id('010').set_color("red")
  if v.get_patch_by_id('110'):
    v.get_patch_by_id('110').set_color("purple")
  if label3 and v.get_patch_by_id('001'):
    v.get_patch_by_id('001').set_color("green") 
    if v.get_patch_by_id('111'):
      v.get_patch_by_id('111').set_color("black") 
  fig = plt.gcf()
  return fig
# return json.dumps(fig_to_dict(fig))

def jaccard_index(set1,set2):
  set1    = set(set1)
  set2    = set(set2)
  intrsct = float(len(set1.intersection(set2)))
  union   = float(len(set1.union(set2)))
  jaccard_index = intrsct/union
  return round(jaccard_index,3)

#inclusion of set1 into ses2
#not symmetric!!!
def inclusion(set1,set2):
  set1    = set(set1)
  set2    = set(set2)
  intrsct = set1.intersection(set2)
  inclusion = len(intrsct)/float(len(set1))
  return int(100*inclusion)

def compute(hubname,hub_names, fun_name):
  hub_readers     = read_list_of_users(hubname)
  similarity_dict = dict()
  for hub in hub_names:
    readers = read_list_of_users(hub)
    #skip itself
    if hub == hubname:
      continue
    if fun_name == "similarity":
      similarity_dict[hub] = jaccard_index(hub_readers,readers)
    if fun_name == "inclusion":
      similarity_dict[hub] = inclusion(hub_readers,readers)
  return similarity_dict

def hub_hist(hub, hub_names):
  fun_name="inclusion"
  values = compute(hub, hub_names, fun_name)
  sorted_values = sorted(values.iteritems(), key=operator.itemgetter(1), reverse=True)
  hubs     = map(lambda x: x[0],sorted_values) 
  y_values = map(lambda x: x[1],sorted_values) 
  MAX_HUBS  = 50
  hubs     = hubs[:MAX_HUBS]
  y_values = y_values[:MAX_HUBS]
  pl.figure()
  ax       = pl.subplot(111)
  hub_range = range(0,MAX_HUBS)
  ax.bar(hub_range, y_values)
  pl.title(hub + " : " + fun_name, fontsize=22)
  pl.xticks(hub_range, hubs,rotation=80)
  pl.ylabel(ylabel, fontsize=20)
  fig = pl.gcf()
  return fig



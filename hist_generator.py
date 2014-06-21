from __future__ import print_function
import glob
import operator
import pylab as pl
from pylab import gca
import os.path
import sys
sys.path.append("src/")
from draw import read_list_of_users


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



def compute(hubname,isCompany,fun_name):
  hub_readers     = read_list_of_users(hubname) 
  hubs_data_dir   = 'data/hubs/'
  tocut           = len(hubs_data_dir)
  hubs            = glob.glob(hubs_data_dir+'*')
  similarity_dict = dict()
  for hub_file in hubs:
    hub     = hub_file[tocut:]
    readers = read_list_of_users(hub)
    #skip itself
    if hub == hubname:
      continue
    if fun_name == "similarity":
      similarity_dict[hub] = jaccard_index(hub_readers,readers)
    if fun_name == "inclusion":
      similarity_dict[hub] = inclusion(hub_readers,readers)
  return similarity_dict


def display_preferences(hubname,isCompany,fun_name):
  ylabel            = fun_name
  values = compute(hubname,isCompany,fun_name)
  sorted_values = sorted(values.iteritems(), key=operator.itemgetter(1), reverse=True)
  hubs     = map(lambda x: x[0],sorted_values) 
  y_values = map(lambda x: x[1],sorted_values) 
  MAX_HUBS  = 50
  #exclude itself
  hubs     = hubs[:MAX_HUBS]
  y_values = y_values[:MAX_HUBS]
  fig      = pl.figure()
  ax       = pl.subplot(111)
  hub_range = range(0,MAX_HUBS)
  fig.subplots_adjust(bottom=0.15)
  ax.bar(hub_range, y_values)
  # re-write and also show % of intersection, like
  # 50% of space also read this...
  pl.xticks(hub_range, hubs,rotation=80)
  pl.ylabel(ylabel, fontsize=20)
#  DefaultSize = fig.get_size_inches()
#  fig.set_size_inches((DefaultSize[0]*1.5, DefaultSize[1]*1.5) )
  pl.savefig("static/img/hubfigures/"+hubname+".png",bbox_inches='tight')
  pl.close()

def save_all_figures():
    csv_hubs = open("data/meta/hubs_name_link.csv","r")
    for line in csv_hubs.readlines():
      name = line.split(",")[1].strip()
      if os.path.isfile("static/img/hubfigures/"+name+".png"):
        print("Figure is already here: " + name)
        continue
      else:
        print("Creating figure for: " + name)
      display_preferences(name,False,"inclusion")

if __name__ == "__main__":
  save_all_figures()

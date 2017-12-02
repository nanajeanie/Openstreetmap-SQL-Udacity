# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 21:03:18 2017

@author: Amy
"""

import sqlite3
import pandas as pd

#%%
conn = sqlite3.connect("C:\\Users\\Amy\\Desktop\\Udacity\\Openstreetmap\\Salt_Lake_County")
Utah = conn.cursor()
#%%

number_nodes = pd.read_sql_query('SELECT COUNT(*) as "Node Count" FROM nodes;',conn)

print "\n",number_nodes.to_string(index=False)

#%%

number_ways = pd.read_sql_query('SELECT COUNT(*) as "Ways Count" FROM ways;',conn)

print "\n",number_ways.to_string(index=False)

#%%

unique_peeps = pd.read_sql_query('SELECT COUNT(DISTINCT("uid")) as "UID Count" \
            FROM (SELECT "uid" FROM nodes UNION ALL SELECT uid FROM ways)',conn)

print "\n",unique_peeps.to_string(index=False)
#%%
top_ten = pd.read_sql_query('SELECT e.user, COUNT(*) as num \
            FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e \
            GROUP BY e.user \
            ORDER BY num DESC \
            LIMIT 10',conn)
print "\n","Top Ten Users","\n",top_ten.to_string(header=False, index = False)
#%%
amenity_type = pd.read_sql_query('SELECT value, COUNT(*) as num \
            FROM nodes_tags UNION ALL SELECT value, Count(*) as num FROM ways_tags\
            WHERE key="amenity" \
            GROUP BY value \
            ORDER BY num DESC \
            LIMIT 10',conn)
print "\n","Top Ten Amenities","\n",amenity_type.to_string(header=False, index = False)
#%%
zip_code = pd.read_sql_query('SELECT tags.value, COUNT(*) as count\
                             FROM (SELECT * FROM nodes_tags \
                             UNION ALL \
                             SELECT * FROM ways_tags) tags \
                             WHERE tags.key="postcode" \
                             GROUP BY tags.value \
                             ORDER BY count DESC;',conn)
print zip_code
#%%

religions = pd.read_sql_query('SELECT nodes_tags.value, COUNT(*) as num \
            FROM nodes_tags \
            JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="place_of_worship") i \
            ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="religion" \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC ',conn)
print "\n","Religions","\n",religions.to_string(header=False, index = False)

#%%

restaurants = pd.read_sql_query('SELECT nodes_tags.value, COUNT(*) as num \
            FROM nodes_tags \
            JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="restaurant") i \
            ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="cuisine" \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC',conn)
print "\n","Restaurants","\n",restaurants.to_string(header=False, index = False)
#%%
#conn.close()
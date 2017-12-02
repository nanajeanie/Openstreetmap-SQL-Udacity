# -*- coding: utf-8 -*-

import re
import xml.etree.cElementTree as ET

def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag not in tags:
            tags[elem.tag] = 1
        else:
            tags[elem.tag] += 1
    print (tags)
    


# In[2]:

#!/usr/bin/env python

utah = "C:\\Users\\Amy\\Desktop\\Udacity\\Openstreetmap\\Salt_Lake_County.osm"


# In[3]:

count_tags(utah)


# In[4]:

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n123456789]')


def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            keys['lower'] += 1
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'] +=1
        elif problemchars.search(element.attrib['k']):
            keys['problemchars'] +=1
        else:
            keys['other'] +=1
    return keys




def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    print (keys)
    return keys

process_map(utah)


# In[5]:

def get_user(element):
    return


def process_user(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if "uid" in element.attrib:
            users.add(element.attrib["uid"])
    return users

process_user(utah)


# In[6]:
# Some addresses have numbers at the end (this is normal), rather than put them all in expected, I am skipping over them.

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
from collections import defaultdict


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "South", "North", "East", "West", "Way", "Circle", "Gateway", "89", "1300",
            "200", "Broadway", "Temple", "Terrace", "Cove", 'Ridge', "Highway","Parkway","Club","Alexander","A",
            "Frontage","Route","Komas","Alley","SR-73","Hope","Village"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Dr.": "Drive",
            "Dr": "Drive",
           "E": "East",
           "W": "West",
           "S": "South",
           "N": "North",
           "Rd": "Road",
           "Sandy":"",
           "Blvd":"Boulevard",
           "Ln": "Lane",
           "Crt":"Court",
           "Cir":"Circle",
           "street":"Street",
           "Wy":"Way",
           "RD":"Road",
           "HWY":"Highway",
           "ST":"Street",
           "Pkwy":"Parkway",
           "S.":"South",
           "N.":"North",
           "W.":"West",
           "E.":"East",
           "Blvd.":"Boulevard",
           "Ln.": "Lane",
           "Crt.":"Court",
           "Cir.":"Circle",
           "street":"Street",
           "Wy.":"Way",
           "RD.":"Road",
           "HWY.":"Highway",
           "ST.":"Street",
           "Pkwy.":"Parkway",
           'Ave.':"Avenue",
           "Pl":"Place",
           "PL":"Place",
           "Pl.":"Place",
           "Ct":"Court",
           "Ct.":"Court",
           "CT":"Court",
           "blvd":"Boulevard",
           "West)":"West"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type[0].isdigit() is True:
            pass
        elif street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r",encoding="utf8")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    looky = street_type_re.search(name)
    if looky:
        street_type = looky.group()
        if street_type not in expected:
            name = re.sub(street_type_re, mapping[street_type], name)
    return name


# In[7]:

audit(utah)


# In[8]:

def test():
    st_types = audit(utah)

    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            print (name, "=>", better_name)
#%%
test()
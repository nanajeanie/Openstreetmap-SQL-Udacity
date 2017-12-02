# -*- coding: utf-8 -*-

import sys
import csv
import codecs
import re
import xml.etree.cElementTree as ET
from collections import defaultdict
import cerberus
import Schema
import pprint
SCHEMA = Schema.schema


# In[2]:

#!/usr/bin/env python

utah = "C:\\Users\\Amy\\Desktop\\Udacity\\Openstreetmap\\Salt_Lake_County.osm"
# In[4]:

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n123456789]')


# In[6]:
# Some addresses have numbers at the end (this is normal), rather than put them all in expected,


street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

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
    return (elem.attrib['k'] == "addr:full")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.items('tag'):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    looky = street_type_re.search(name)
    if looky:
        street_type = looky.group()
        if street_type[0].isdigit() is True:
            return name
        if street_type not in expected:
            name = re.sub(street_type_re, mapping[street_type], name)
            return name




# In[25]:

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def load_new_tag(element, secondary, default_tag_type):
    """
    Load a new tag dict to go into the list of dicts for way_tags, node_tags
    """
    new = {}
    new['id'] = element.attrib['id']
    if ":" not in secondary.attrib['k']:
        new['key'] = secondary.attrib['k']
        new['type'] = default_tag_type
    else:
        post_colon = secondary.attrib['k'].index(":") + 1
        new['key'] = secondary.attrib['k'][post_colon:]
        new['type'] = secondary.attrib['k'][:post_colon - 1]
    new['value'] = secondary.attrib['v']
    #print secondary.attrib['v']
    return new

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for attrib, value in element.attrib.items():
            if attrib in node_attr_fields is None:
                node_attribs[attrib] = "9999999"
            else:
                node_attribs[attrib] = value

        # for elements within the top element
        for secondary in element.iter('tag'):
            if secondary.tag == 'tag':
                if problem_chars.match(secondary.attrib['k']) is not None:
                    continue
                elif secondary.attrib['k'] == 'addr:street':
                    new = update_name(secondary.attrib['v'], mapping)
                    tags.append(new)
                else:
                    new = load_new_tag(element, secondary, default_tag_type)
                    tags.append(new)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for attrib, value in element.attrib.items():
            if attrib in way_attr_fields:
                way_attribs[attrib] = value

        counter = 0
        for secondary in element.iter('tag'):
            if secondary.tag == 'tag':
                if problem_chars.match(secondary.attrib['k']) is not None:
                    continue
                elif secondary.attrib['k'] == 'addr:street':
                    new = update_name(secondary.attrib['v'], mapping)
                    tags.append(new)
                else:
                    new = load_new_tag(element, secondary, default_tag_type)
                    tags.append(new)

        for k in element.iter('nd'):
            d = {'id':element.attrib['id']}
            d['node_id'] = k.attrib['ref']
            d['position'] = counter
            way_nodes.append(d)
            counter += 1        # print {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}



# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(iter(validator.errors.items()))
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        try:
            super(UnicodeDictWriter, self).writerow({
                    k: (v.encode('utf-8') if isinstance(v, str) else v) for k, v in row.items()
                    })
        except:
            pass


    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# ================================================== #
#              Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    for i in range(1,80):
        process_map(utah,validate=False)
        sys.stdout.write('.'); sys.stdout.flush();

# In[ ]:
print ("tada")
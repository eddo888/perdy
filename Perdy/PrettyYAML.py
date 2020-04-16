#!/usr/bin/env python3

import yaml

from datetime import datetime, timedelta

#_____________________________________________________
def representer_unicode(dumper, uni):
    node = yaml.ScalarNode(tag='tag:yaml.org,2002:str', value=uni)
    return node

def datetime_representer(dumper, dt):
    node = yaml.ScalarNode(tag='tag:yaml.org,2002:timestamp', value=dt.strftime('%Y-%m-%dT%H:%M:%S'))
    return node
    
# http://stackoverflow.com/questions/16782112/can-pyyaml-dump-dict-items-in-non-alphabetical-order

def represent_ordereddict(dumper, data):
    value = []

    def add(item_key):
        item_value=data[item_key]
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)
        value.append((node_key, node_value))
        
    for item_key in sorted(data.keys()):
        if item_key.startswith('_'):
            add(item_key)

    for item_key in sorted(data.keys()):
        if not item_key.startswith('_'):
            add(item_key)
            
    return yaml.nodes.MappingNode('tag:yaml.org,2002:map', value)

def loadRepresenters():
    yaml.add_representer(str, representer_unicode)
    yaml.add_representer(datetime, datetime_representer)
    yaml.add_representer(dict,represent_ordereddict)


from collections import defaultdict
import json
import pprint
import os
import sys

class Item:
    def __init__(self, ident, reference):
        self.ident = ident
        self.reference = reference
        # you can create objects like this.
        # worldmap.put_object_at_position(Item(ItemManager.ITEM_TYPES[str(item['item'])]['ident']), Position)


class ItemManager:
    def __init__(self):
        self.ITEM_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/items/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    with open(root+'/'+file_data, encoding='utf-8') as data_file:
                        data = json.load(data_file)
                    for item in data:
                        try:
                            for key, value in item.items():
                                if(isinstance(value, list)):
                                    self.ITEM_TYPES[item['ident']][key] = []
                                    for add_value in value:
                                        self.ITEM_TYPES[item['ident']][key].append(str(add_value))
                                else:
                                    self.ITEM_TYPES[item['ident']][key] = str(value)
                        except Exception:
                            print()
                            print('!! couldn\'t parse: ' + str(item) + ' -- likely missing ident.')
                            print()
                            sys.exit()
        print('total ITEM_TYPES loaded: ' + str(len(self.ITEM_TYPES)))

# Copyright 2016 Dave Kludt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from cap.helper import normalize, slug
from flask import g


import re


class Product:
    def __init__(self, data):
        self.id = data.get('_id')
        self.title = normalize(data.get('title'))
        self.db_name = data.get('db_name')
        self.us_url = data.get('us_url')
        self.uk_url = data.get('uk_url')
        self.doc_url = data.get('doc_url')
        self.pitchfork_url = data.get('pitchfork_url')
        self.require_region = bool(data.get('require_region'))
        self.active = bool(data.get('active'))
        self.limit_maps = self.get_defined_limit_maps(data)

    def set_db_name(self):
        temp = re.sub(' +', ' ', str(self.title.lower().strip()))
        self.db_name = re.sub(' ', '_', temp)

    def save_dict(self):
        temp = self.__dict__
        del temp['id']
        del temp['limit_maps']
        return temp

    def get_defined_limit_maps(self, data):
        temp = []
        limit_maps = g.db.limit_maps.find(
            {
                'product': self.db_name,
                'active': True
            }
        )
        if limit_maps.count() > 0:
            for limit in limit_maps:
                temp.append(Limit(limit))

        return temp


class Limit:
    def __init__(self, data):
        self.product = data.get('product')
        self.title = normalize(data.get('title'))
        self.uri = data.get('uri')
        self.absolute_path = data.get('absolute_path')
        self.absolute_type = data.get('absolute_type')
        self.limit_key = data.get('limit_key')
        self.value_key = data.get('value_key')
        self.active = bool(data.get('active'))
        self.id = data.get('_id')
        self.slug = slug(data.get('title'))

    def save_dict(self):
        temp = self.__dict__
        del temp['id']
        return temp


class Region:
    def __init__(self, data):
        self.abbreviation = data.get('abbreviation').upper()
        self.name = data.get('name')

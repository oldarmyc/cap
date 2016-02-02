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


from future.utils import iteritems
from flask import session, g
from dateutil import tz


import datetime
import re


UTC = tz.tzutc()


def slug(string):
    if string:
        temp = re.sub(' +', ' ', string.lower())
        return re.sub(' ', '_', temp)


def normalize(string):
    if string:
        return re.sub('\s+', ' ', string.strip())


def log_entry(data):
    # Removing data elements we do not need
    ddi = data.pop('ddi')
    region = data.pop('region')
    del data['csrf_token']
    del data['token']

    products_queried = []
    for product, value in iteritems(data):
        if str(value) == 'y':
            products_queried.append(product)

    store_data = {
        'ddi': ddi,
        'region': region,
        'queried': products_queried,
        'query_results': [],
        'queried_at': datetime.datetime.now(UTC),
        'queried_by': session.get('username')
    }
    log_id = g.db.query_logs.insert(store_data)
    return log_id

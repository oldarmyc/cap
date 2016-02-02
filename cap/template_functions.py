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


from cap.models import Product
from flask import g


def view_functions():

    def get_product_title(db_name):
        temp_product = g.db.products.find_one({'db_name': db_name})
        if temp_product:
            return temp_product.get('title')
        return ''

    def get_limit_maps(product):
        limit_maps = g.db.limit_maps.find(
            {
                'product': product.get('db_name'),
                'active': True
            }
        )
        return limit_maps

    def generate_product_data(results):
        temp_product = g.db.products.find_one(
            {
                'db_name': list(results)[0]
            }
        )
        if temp_product:
            return Product(temp_product)
        return None

    def determine_color_class(limit, used):
        percentage = float(used/float(limit))
        display_percentage = "{0:.0f}%".format(percentage * 100)
        if percentage < 0.6:
            css_class = 'text-success'
        elif percentage > 0.8:
            css_class = 'text-danger limit-alert-text-danger'
        else:
            css_class = 'text-warning limit-alert-text-warning'
        return display_percentage, css_class

    return dict(
        get_product_title=get_product_title,
        get_limit_maps=get_limit_maps,
        generate_product_data=generate_product_data,
        determine_color_class=determine_color_class
    )

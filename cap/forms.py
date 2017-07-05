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

try:
    from flask_wtf import FlaskForm as Form
except:
    from flask.ext.wtf import Form

from wtforms import fields, validators
from cap.helper import slug
from flask import g


import re


class ManageProduct(Form):
    title = fields.TextField('Title:', validators=[validators.required()])
    us_url = fields.TextField(
        'US URL:',
        validators=[validators.required()]
    )
    uk_url = fields.TextField(
        'UK URL:',
        validators=[validators.required()]
    )
    doc_url = fields.TextField(
        'Docs URL:',
        validators=[validators.required()]
    )
    pitchfork_url = fields.TextField('Pitchfork URL:')
    require_region = fields.BooleanField('Require Region:')
    active = fields.BooleanField('Active to Use:')
    db_name = fields.HiddenField()


class RegionSet(Form):
    name = fields.TextField('Name:', validators=[validators.required()])
    abbreviation = fields.TextField(
        'Abbreviation:',
        validators=[validators.required()]
    )

    def validate_abbreviation(self, field):
        found = g.db.settings.find_one(
            {
                'regions.abbreviation': self.abbreviation.data.upper()
            }
        )
        if found:
            raise validators.ValidationError('Duplicate abbreviation')

    def validate_name(self, field):
        regex = re.compile(
            '^%s$' % self.name.data,
            re.IGNORECASE
        )
        found = g.db.settings.find_one({'regions.name': regex})
        if found:
            raise validators.ValidationError('Duplicate name')


class LimitMap(Form):
    slug = fields.HiddenField()
    id = fields.HiddenField()
    product = fields.SelectField(
        'Product:',
        choices=[('', '')],
        validators=[validators.required()]
    )
    title = fields.TextField(
        'Title:',
        validators=[validators.required()]
    )
    uri = fields.TextField(
        'URI:',
        validators=[validators.required()]
    )
    absolute_path = fields.TextField(
        'Path:',
        validators=[validators.required()]
    )
    absolute_type = fields.SelectField(
        'Absolute Type:',
        choices=[
            ('', ''),
            ('dict', 'Dictionary'),
            ('list', 'List')
        ],
        validators=[validators.required()]
    )
    limit_key = fields.TextField('Limit Key:')
    value_key = fields.TextField('Value Key:')
    active = fields.BooleanField('Active:')

    def validate_title(self, field):
        found = g.db.limit_maps.find_one(
            {
                'product': self.product.data,
                'slug': slug(self.title.data)
            }
        )
        if found:
            if str(found.get('_id')) != str(self.id.data):
                raise validators.ValidationError('Duplicate limit')

    def validate_uri(self, field):
        found = g.db.limit_maps.find_one(
            {
                'uri': self.uri.data.strip().lower(),
                'absolute_path': self.absolute_path.data.strip().lower(),
                'limit_key': self.limit_key.data.strip().lower()
            }
        )
        if found:
            if str(found.get('_id')) != str(self.id.data):
                raise validators.ValidationError(
                    'Duplicate URI with path and key'
                )


class BaseForm(Form):
    pass


def generate_limits_form(products):
    class F(BaseForm):
        pass

    for product in products:
        setattr(
            F,
            str(product.get('db_name')),
            fields.BooleanField(
                str(product.get('title')),
                description=str(product.get('title'))
            )
        )

    return F()

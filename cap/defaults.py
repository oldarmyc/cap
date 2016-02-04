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


from flask.ext.cloudadmin.defaults import check_and_initialize
from cap.config import config


def application_initialize(db, app):
    settings = db.settings.find_one()
    if settings is None:
        # Initialize admin first then setup application
        settings = check_and_initialize(app=app, database=db)

    if settings.get('application_set') is None:
        app.logger.debug(
            'Application settings are empty...initializing'
        )
        db.settings.update(
            {},
            {
                '$set': {
                    'app_title': 'Cap',
                    'app_well': (
                        '<p class="lead">Cloud Limits Aggregator'
                        '</p><div>For improvements or suggestions please go to'
                        ' GitHub and submit an <a href="https://github.'
                        'com/oldarmyc/cap/issues/new" '
                        'target="_blank" title="Submit a GitHub issue">issue'
                        '</a></div><p></p>'
                    ),
                    'app_footer': (
                        'This site is not officially supported by Rackspace. '
                        'Source is available on <a href="https://github.com/'
                        'oldarmyc/cap/" class="tooltip-title" '
                        'target="_blank" title="Cap Repository">github</a>'
                    ),
                    'admins': [
                        {
                            'username': config.ADMIN_USERNAME,
                            'active': True,
                            'name': config.ADMIN_NAME,
                            'email': config.ADMIN_EMAIL
                        }
                    ],
                    'regions': [
                        {
                            'abbreviation': 'DFW',
                            'name': 'Dallas'
                        }, {
                            'abbreviation': 'ORD',
                            'name': 'Chicago'
                        }, {
                            'abbreviation': 'IAD',
                            'name': 'Virginia'
                        }, {
                            'abbreviation': 'SYD',
                            'name': 'Sydney'
                        }, {
                            'abbreviation': 'LON',
                            'name': 'London'
                        }, {
                            'abbreviation': 'HKG',
                            'name': 'Hong Kong'
                        }
                    ],
                    'roles': [
                        {
                            'active': True,
                            'name': 'Administrators',
                            'slug': 'administrators'
                        }, {
                            'active': True,
                            'name': 'Logged In',
                            'slug': 'logged_in',
                            'perms': [
                                '/',
                                '/query/',
                                '/query/status/<task_id>',
                                '/admin/logout/',
                            ]
                        }, {
                            'active': True,
                            'name': 'All',
                            'slug': 'all',
                            'perms': [
                                '/',
                                '/admin/login',
                                '/admin/login/check'
                            ]
                        },
                    ],
                    "menu": [
                        {
                            "name": "Query Limits",
                            "parent": "",
                            "url": "/query/",
                            "parent_order": 1,
                            "db_name": "query",
                            "active": True,
                            "divider": False,
                            "order": 2,
                            "permissions": "logged_in"
                        }, {
                            "url": "/admin/users/admins",
                            "db_name": "manage_admins",
                            "name": "Manage Admins",
                            "parent": "system",
                            "active": True,
                            "parent_order": 2,
                            "order": 1,
                            "permissions": "administrators"
                        }, {
                            "url": "/admin/users/exemptions",
                            "db_name": "manage_exemptions",
                            "name": "Manage Exemptions",
                            "parent": "system",
                            "active": True,
                            "parent_order": 2,
                            "order": 2,
                            "permissions": "administrators",
                            "divider": True
                        }, {
                            "name": "Manage Products",
                            "parent": "system",
                            "url": "/manage/products",
                            "parent_order": 2,
                            "db_name": "manage_products",
                            "active": True,
                            "divider": False,
                            "order": 3,
                            "permissions": "administrators"
                        }, {
                            "name": "Manage Limits",
                            "parent": "system",
                            "url": "/manage/limits",
                            "parent_order": 2,
                            "db_name": "manage_limits",
                            "active": True,
                            "divider": False,
                            "order": 4,
                            "permissions": "administrators"
                        }, {
                            "name": "Manage Regions",
                            "parent": "system",
                            "url": "/manage/regions",
                            "parent_order": 2,
                            "db_name": "manage_regions",
                            "active": True,
                            "divider": False,
                            "order": 5,
                            "permissions": "administrators"
                        }, {
                            "url": "/admin/general/",
                            "db_name": "general_settings",
                            "name": "General Settings",
                            "parent": "administrators",
                            "active": True,
                            "parent_order": 3,
                            "order": 1,
                            "permissions": "administrators"
                        }, {
                            "url": "/admin/menu/",
                            "db_name": "menu_settings",
                            "name": "Menu Settings",
                            "parent": "administrators",
                            "active": True,
                            "parent_order": 3,
                            "order": 2,
                            "permissions": "administrators"
                        }, {
                            "url": "/admin/roles",
                            "db_name": "manage_roles",
                            "name": "Manage Roles",
                            "parent": "administrators",
                            "active": True,
                            "parent_order": 3,
                            "order": 3,
                            "permissions": "administrators"
                        }
                    ]
                }
            }
        )

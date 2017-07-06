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


from flask_cloudadmin.defaults import check_and_initialize
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
        limit_maps = [
            {
                'product': 'servers',
                'title': 'Servers',
                'uri': '/v2/{ddi}/limits',
                'slug': 'servers',
                'active': True,
                'path': 'absolute["maxTotalInstances"]',
                'absolute_path': 'limits.absolute',
                'value_key': '',
                'absolute_type': 'dict',
                'limit_key': 'maxTotalInstances'
            }, {
                'product': 'servers',
                'title': 'Ram - MB',
                'uri': '/v2/{ddi}/limits',
                'slug': 'ram_-_mb',
                'active': True,
                'path': 'absolute["maxTotalRAMSize"]',
                'absolute_path': 'limits.absolute',
                'value_key': '',
                'absolute_type': 'dict',
                'limit_key': 'maxTotalRAMSize'
            }, {
                'product': 'servers',
                'title': 'Private Networks',
                'uri': '/v2/{ddi}/limits',
                'slug': 'private_networks',
                'active': True,
                'path': 'absolute["maxTotalPrivateNetworks"]',
                'absolute_path': 'limits.absolute',
                'value_key': '',
                'absolute_type': 'dict',
                'limit_key': 'maxTotalPrivateNetworks'
            }, {
                'product': 'load_balancers',
                'title': 'Total Load Balancers',
                'uri': '/v1.0/{ddi}/loadbalancers/absolutelimits',
                'slug': 'total_load_balancers',
                'active': True,
                'path': 'absolute["LOADBALANCER_LIMIT"]',
                'absolute_path': 'absolute',
                'value_key': '',
                'absolute_type': 'list',
                'limit_key': 'LOADBALANCER_LIMIT'
            }, {
                'product': 'load_balancers',
                'title': 'Nodes per LB',
                'uri': '/v1.0/{ddi}/loadbalancers/absolutelimits',
                'slug': 'nodes_per_lb',
                'active': True,
                'path': 'absolute["NODE_LIMIT"]',
                'absolute_path': 'absolute',
                'value_key': '',
                'absolute_type': 'list',
                'limit_key': 'NODE_LIMIT'
            }, {
                'product': 'load_balancers',
                'title': 'Access Lists per LB',
                'absolute_path': 'absolute',
                'uri': '/v1.0/{ddi}/loadbalancers/absolutelimits',
                'slug': 'access_lists_per_lb',
                'value_key': '',
                'absolute_type': 'list',
                'active': True,
                'limit_key': 'ACCESS_LIST_LIMIT'
            }, {
                'product': 'load_balancers',
                'title': 'Certificate Mappings per LB',
                'absolute_path': 'absolute',
                'uri': '/v1.0/{ddi}/loadbalancers/absolutelimits',
                'slug': 'certificate_mappings_per_lb',
                'value_key': '',
                'absolute_type': 'list',
                'active': True,
                'limit_key': 'CERTIFICATE_MAPPING_LIMIT'
            }, {
                'product': 'cbs',
                'title': 'SATA - GB',
                'absolute_path': 'quota_set.gigabytes_SATA',
                'uri': '/v1/{ddi}/os-quota-sets/{ddi}?usage=True',
                'slug': 'sata_-_gb',
                'value_key': 'in_use',
                'absolute_type': 'dict',
                'active': True,
                'limit_key': 'limit'
            }, {
                'product': 'cbs',
                'title': 'SSD - GB',
                'absolute_path': 'quota_set.gigabytes_SSD',
                'uri': '/v1/{ddi}/os-quota-sets/{ddi}?usage=True',
                'slug': 'ssd_-_gb',
                'value_key': 'in_use',
                'absolute_type': 'dict',
                'active': True,
                'limit_key': 'limit'
            }, {
                'product': 'autoscale',
                'title': 'Max Groups',
                'absolute_path': 'limits.absolute',
                'uri': '/v1.0/{ddi}/limits',
                'slug': 'max_groups',
                'value_key': '',
                'absolute_type': 'dict',
                'active': True,
                'limit_key': 'maxGroups'
            }, {
                'product': 'autoscale',
                'title': 'Policies per Group',
                'absolute_path': 'limits.absolute',
                'uri': '/v1.0/{ddi}/limits',
                'slug': 'policies_per_group',
                'value_key': '',
                'absolute_type': 'dict',
                'active': True,
                'limit_key': 'maxPoliciesPerGroup'
            }, {
                'product': 'autoscale',
                'title': 'Webhooks per Policy',
                'absolute_path': 'limits.absolute',
                'uri': '/v1.0/{ddi}/limits',
                'slug': 'webhooks_per_policy',
                'value_key': '',
                'absolute_type': 'dict',
                'active': True,
                'limit_key': 'maxWebhooksPerPolicy'
            }, {
                'product': 'dns',
                'title': 'Domains',
                'limit_key': 'domains',
                'absolute_path': 'limits.absolute',
                'uri': '/v1.0/{ddi}/limits',
                'slug': 'domains',
                'value_key': '',
                'absolute_type': 'dict',
                'active': True
            }, {
                'product': 'dns',
                'title': 'Record per Domain',
                'limit_key': 'records per domain',
                'absolute_path': 'limits.absolute',
                'uri': '/v1.0/{ddi}/limits',
                'slug': 'record_per_domain',
                'value_key': '',
                'absolute_type': 'dict',
                'active': True
            }
        ]
        if db.limit_maps.count() == 0:
            for item in limit_maps:
                db.limit_maps.insert(item)

        products = [
            {
                'limit_maps': [],
                'title': 'Load Balancers',
                'us_url': (
                    'https://{region}.loadbalancers.api.rackspacecloud.com'
                ),
                'active': True,
                'db_name': 'load_balancers',
                'uk_url': (
                    'https://{region}.loadbalancers.api.rackspacecloud.com'
                ),
                'require_region': True,
                'doc_url': (
                    'https://developer.rackspace.com/docs/cloud-load-'
                    'balancers/v1/general-api-info/limits/#rate-limits'
                ),
                'pitchfork_url': (
                    'https://pitchfork.cloudapi.co/'
                    'load_balancers/#get_limits-load_balancers'
                )
            }, {
                'title': 'Servers',
                'us_url': 'https://{region}.servers.api.rackspacecloud.com',
                'active': True,
                'db_name': 'servers',
                'uk_url': 'https://{region}.servers.api.rackspacecloud.com',
                'require_region': True,
                'doc_url': (
                    'https://developer.rackspace.com/docs/cloud-servers'
                    '/v2/general-api-info/limits/#rate-limits'
                ),
                'limit_uri': '/limits',
                'limit_maps': [],
                'pitchfork_url': (
                    'https://pitchfork.cloudapi.co/'
                    'servers/#get_limits-cloud_servers'
                )
            }, {
                'limit_maps': [],
                'title': 'Block Storage',
                'pitchfork_url': (
                    'https://pitchfork.cloudapi.co/cbs/#show_quota_usage-cbs'
                ),
                'us_url': (
                    'https://{region}.blockstorage.api.rackspacecloud.com'
                ),
                'active': True,
                'db_name': 'cbs',
                'uk_url': (
                    'https://{region}.blockstorage.api.rackspacecloud.com'
                ),
                'require_region': True,
                'doc_url': (
                    'https://developer.rackspace.com/docs/cloud-block-'
                    'storage/v1/general-api-info/cloud-block-storage-quotas/'
                )
            }, {
                'title': 'Autoscale',
                'pitchfork_url': (
                    'https://pitchfork.cloudapi.co/autoscale'
                    '/#get_limits-autoscale'
                ),
                'us_url': 'https://{region}.autoscale.api.rackspacecloud.com',
                'active': True,
                'db_name': 'autoscale',
                'uk_url': 'https://{region}.autoscale.api.rackspacecloud.com',
                'require_region': True,
                'doc_url': (
                    'https://developer.rackspace.com/docs/autoscale/'
                    'v1/developer-guide/#document-general-api-info/limits'
                )
            }, {
                'title': 'DNS',
                'pitchfork_url': (
                    'https://pitchfork.cloudapi.co/dns/#list_all_limits-dns'
                ),
                'us_url': 'https://dns.api.rackspacecloud.com',
                'active': True,
                'db_name': 'dns',
                'uk_url': 'https://lon.dns.api.rackspacecloud.com',
                'require_region': True,
                'doc_url': (
                    'https://developer.rackspace.com/docs/cloud-dns'
                    '/v1/general-api-info/limits/#rate-limits'
                )
            }
        ]
        if db.products.count() == 0:
            for item in products:
                db.products.insert(item)

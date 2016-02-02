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


sample_product = {
    "title": "Test",
    "us_url": "http://us.test.com",
    "uk_url": "http://uk.test.com",
    "active": True,
    "db_name": "test",
    "require_region": True,
    "doc_url": "http://doc.test.com",
    "pitchfork_url": "https://pitchfork/url"
}

sample_limit = {
    "product": "test",
    "title": "Test",
    "uri": "/limits",
    "slug": "test",
    "active": True,
    "absolute_path": "test/path",
    "absolute_type": "list",
    "limit_key": "test_limit",
    "value_key": "test_value"
}

sample_log = {
    "queried": ["dns"],
    "queried_by": "skeletor",
    "region": "dfw",
    "ddi": "123456",
    'query_results': []
}

sample_auth_failure = {
    'message': (
        '<strong>Error!</strong> Authentication has failed due to'
        ' incorrect token or DDI. Please check the token and DDI '
        'and try again.'
    )
}

""" DNS Tests """

dns = {
    "title": "DNS",
    "us_url": "https://us.test.com",
    "uk_url": "https://uk.test.com",
    "active": True,
    "db_name": "dns",
    "require_region": True,
    "doc_url": "https://doc.test.com",
    "pitchfork_url": "https://pitchfork.url",
    "limit_maps": []
}

dns_limit = {
    "product": "dns",
    "title": "Domains",
    "uri": "/limits",
    "slug": "domains",
    "active": True,
    "absolute_path": "limits.absolute",
    "absolute_type": "dict",
    "value_key": "",
    "limit_key": "domains"
}

dns_limit_return = {
    "limits": {
        "rate": [
            {
                "regex": ".*/v\\d+\\.\\d+/(\\d+/domains/search).*",
                "limit": [
                    {
                        "value": 20,
                        "verb": "GET",
                        "next-available": "2016-01-12T13:56:11.450Z",
                        "remaining": 20,
                        "unit": "MINUTE"
                    }
                ],
                "uri": "*/domains/search*"
            }
        ],
        "absolute": {
            "domains": 500,
            "records per domain": 500
        }
    }
}

dns_list_return = {
    "domains": [
        {
            "comment": "Test",
            "updated": "2015-12-08T20:47:02.000+0000",
            "name": "test.net",
            "created": "2015-04-09T15:42:49.000+0000",
            "emailAddress": "skeletor@rackspace.com",
            "id": 123465798,
            "accountId": 1234567
        }
    ],
    "totalEntries": 1
}

dns_full_return = {
    'dns': {
        'values': {'Domains': 1},
        'limits': {'Domains': 500}
    }
}

""" Autoscale """

autoscale = {
    "title": "Autoscale",
    "us_url": "https://us.test.com",
    "uk_url": "https://uk.test.com",
    "active": True,
    "db_name": "autoscale",
    "require_region": True,
    "doc_url": "https://doc.test.com",
    "pitchfork_url": "https://pitchfork.url",
    "limit_maps": []
}

autoscale_limit = {
    "product": "autoscale",
    "title": "Max Groups",
    "absolute_path": "limits.absolute",
    "uri": "/v1.0/{ddi}/limits",
    "slug": "max_groups",
    "value_key": "",
    "absolute_type": "dict",
    "active": True,
    "limit_key": "maxGroups"
}

autoscale_limit_return = {
    "limits": {
        "rate": [
            {
                "regex": "/v1\\.0/execute/(.*)",
                "limit": [
                    {
                        "value": 10,
                        "verb": "ALL",
                        "next-available": "2016-01-12T14:51:13.402Z",
                        "remaining": 10,
                        "unit": "SECOND"
                    }
                ],
                "uri": "/v1.0/execute/*"
            }
        ],
        "absolute": {
            "maxGroups": 1000,
            "maxPoliciesPerGroup": 100,
            "maxWebhooksPerPolicy": 25
        }
    }
}

autoscale_list_return = {
    "groups": [
        {
            "state": {
                "status": "ACTIVE",
                "desiredCapacity": 0,
                "paused": False,
                "active": [],
                "pendingCapacity": 0,
                "activeCapacity": 0,
                "name": "test"
            },
            "id": "d446f3c2-612f-41b8-92dc-4d6e1422bde2",
            "links": [
                {
                    "href": (
                        'https://dfw.autoscale.api.rackspacecloud.com/v1.0'
                        '/1234567/groups/d446f3c2-612f-41b8-92dc-4d6e1422bde2/'
                    ),
                    "rel": "self"
                }
            ]
        }
    ],
    "groups_links": []
}

autoscale_full_return = {
    'autoscale': {
        'values': {'Max Groups': 1},
        'limits': {'Max Groups': 1000}
    }
}

""" Big Data """

big_data = {
    "title": "Big Data",
    "us_url": "https://us.test.com",
    "uk_url": "https://uk.test.com",
    "active": True,
    "db_name": "big_data",
    "require_region": True,
    "doc_url": "https://doc.test.com",
    "pitchfork_url": "https://pitchfork.url",
    "limit_maps": []
}

big_data_limit = [
    {
        "product": "big_data",
        "title": "Node Count",
        "absolute_path": "limits.absolute.node_count",
        "uri": "/v2/{ddi}/limits",
        "slug": "node_count",
        "value_key": "remaining",
        "absolute_type": "dict",
        "active": True,
        "limit_key": "limit"
    }, {
        "product": "big_data",
        "title": "Disk - MB",
        "absolute_path": "limits.absolute.disk",
        "uri": "/v2/{ddi}/limits",
        "slug": "disk_-_mb",
        "value_key": "remaining",
        "absolute_type": "dict",
        "active": True,
        "limit_key": "limit"
    }
]

big_data_limit_return = {
    "limits": {
        "absolute": {
            "node_count": {
                "limit": 15,
                "remaining": 8
            },
            "disk": {
                "limit": 50000,
                "remaining": 25000
            },
            "ram": {
                "limit": 655360,
                "remaining": 555360
            },
            "vcpus": {
                "limit": 200,
                "remaining": 120
            }
        }
    }
}

big_data_full_return = {
    'big_data': {
        'values': {'Node Count': 7, 'Disk - MB': 25000},
        'limits': {'Node Count': 15, 'Disk - MB': 50000}
    }
}

""" CBS """

cbs = {
    "title": "CBS",
    "us_url": "https://us.test.com",
    "uk_url": "https://uk.test.com",
    "active": True,
    "db_name": "cbs",
    "require_region": True,
    "doc_url": "https://doc.test.com",
    "pitchfork_url": "https://pitchfork.url",
    "limit_maps": []
}

cbs_limit = {
    "product": "cbs",
    "title": "SATA - GB",
    "absolute_path": "quota_set.gigabytes_SATA",
    "uri": "/v1/{ddi}/os-quota-sets/{ddi}?usage=True",
    "slug": "sata_-_gb",
    "value_key": "in_use",
    "absolute_type": "dict",
    "active": True,
    "limit_key": "limit"
}

cbs_limit_return = {
    "quota_set": {
        "volumes": {
            "limit": -1,
            "reserved": 0,
            "in_use": 3
        },
        "gigabytes_SATA": {
            "limit": 10240,
            "reserved": 0,
            "in_use": 325
        },
        "gigabytes_SSD": {
            "limit": 10240,
            "reserved": 0,
            "in_use": 50
        }
    }
}

cbs_full_return = {
    'cbs': {
        'values': {'SATA - GB': 9915},
        'limits': {'SATA - GB': 10240}
    }
}

""" Load Balancers """

clb = {
    "title": "Load Balancers",
    "us_url": "https://us.test.com",
    "uk_url": "https://uk.test.com",
    "active": True,
    "db_name": "load_balancers",
    "require_region": True,
    "doc_url": "https://doc.test.com",
    "pitchfork_url": "https://pitchfork.url",
    "limit_maps": []
}

clb_limit = [
    {
        "product": "load_balancers",
        "title": "Total Load Balancers",
        "uri": "/v1.0/{ddi}/loadbalancers/absolutelimits",
        "slug": "total_load_balancers",
        "active": True,
        "path": "absolute['LOADBALANCER_LIMIT']",
        "absolute_path": "absolute",
        "value_key": "",
        "absolute_type": "list",
        "limit_key": "LOADBALANCER_LIMIT"
    }, {
        "product": "load_balancers",
        "title": "Nodes per LB",
        "uri": "/v1.0/{ddi}/loadbalancers/absolutelimits",
        "slug": "nodes_per_lb",
        "active": True,
        "path": "absolute['NODE_LIMIT']",
        "absolute_path": "absolute",
        "value_key": "",
        "absolute_type": "list",
        "limit_key": "NODE_LIMIT"
    }
]

clb_limit_return = {
    "absolute": [
        {
            "name": "IPV6_LIMIT",
            "value": 25
        }, {
            "name": "LOADBALANCER_LIMIT",
            "value": 25
        }, {
            "name": "BATCH_DELETE_LIMIT",
            "value": 10
        }, {
            "name": "ACCESS_LIST_LIMIT",
            "value": 100
        }, {
            "name": "NODE_LIMIT",
            "value": 25
        }, {
            "name": "NODE_META_LIMIT",
            "value": 25
        }, {
            "name": "LOADBALANCER_META_LIMIT",
            "value": 25
        }, {
            "name": "CERTIFICATE_MAPPING_LIMIT",
            "value": 20
        }
    ]
}

clb_list_return = {
    "loadBalancers": [
        {
            "status": "ACTIVE",
            "updated": {
                "time": "2016-01-12T16:04:44Z"
            },
            "protocol": "HTTP",
            "name": "test",
            "algorithm": "LEAST_CONNECTIONS",
            "created": {
                "time": "2016-01-12T16:04:44Z"
            },
            "virtualIps": [
                {
                    "ipVersion": "IPV4",
                    "type": "PUBLIC",
                    "id": 19875,
                    "address": "148.62.0.226"
                }, {
                    "ipVersion": "IPV6",
                    "type": "PUBLIC",
                    "id": 9318325,
                    "address": "2001:4800:7904:0100:f46f:211b:0000:0001"
                }
            ],
            "id": 506497,
            "timeout": 30,
            "nodeCount": 0,
            "port": 80
        }
    ]
}

clb_full_return = {
    'load_balancers': {
        'values': {'Total Load Balancers': 1},
        'limits': {'Total Load Balancers': 25, 'Nodes per LB': 25}
    }
}

""" Servers """

server = {
    "title": "Servers",
    "us_url": "https://us.test.com",
    "uk_url": "https://uk.test.com",
    "active": True,
    "db_name": "servers",
    "require_region": True,
    "doc_url": "https://doc.test.com",
    "pitchfork_url": "https://pitchfork.url",
    "limit_maps": []
}

server_limit = [
    {
        "product": "servers",
        "title": "Servers",
        "uri": "/v2/{ddi}/limits",
        "slug": "servers",
        "active": True,
        "path": "absolute['maxTotalInstances']",
        "absolute_path": "limits.absolute",
        "value_key": "",
        "absolute_type": "dict",
        "limit_key": "maxTotalInstances"
    }, {
        "product": "servers",
        "title": "Private Networks",
        "uri": "/v2/{ddi}/limits",
        "slug": "private_networks",
        "active": True,
        "path": "absolute['maxTotalPrivateNetworks']",
        "absolute_path": "limits.absolute",
        "value_key": "",
        "absolute_type": "dict",
        "limit_key": "maxTotalPrivateNetworks"
    }, {
        "product": "servers",
        "title": "Ram - MB",
        "uri": "/v2/{ddi}/limits",
        "slug": "ram_-_mb",
        "active": True,
        "path": "absolute['maxTotalRAMSize']",
        "absolute_path": "limits.absolute",
        "value_key": "",
        "absolute_type": "dict",
        "limit_key": "maxTotalRAMSize"
    }
]

server_limit_return = {
    "limits": {
        "rate": [
            {
                "regex": "/[^/]*/?$",
                "limit": [
                    {
                        "next-available": "2016-01-12T16:14:47.624Z",
                        "unit": "MINUTE",
                        "verb": "GET",
                        "remaining": 2200,
                        "value": 2200
                    }
                ],
                "uri": "*"
            }, {
                "regex": (
                    "/v[^/]+/[^/]+/servers/([^/]+)/rax-si-image-schedule"
                ),
                "limit": [
                    {
                        "next-available": "2016-01-12T16:14:47.624Z",
                        "unit": "SECOND",
                        "verb": "POST",
                        "remaining": 10,
                        "value": 10
                    }
                ],
                "uri": "/servers/{id}/rax-si-image-schedule"
            }
        ],
        "absolute": {
            "maxPersonalitySize": 1000,
            "maxTotalCores": -1,
            "maxPersonality": 5,
            "totalPrivateNetworksUsed": 1,
            "maxImageMeta": 40,
            "maxTotalPrivateNetworks": 10,
            "maxSecurityGroupRules": -1,
            "maxTotalKeypairs": 100,
            "totalRAMUsed": 4096,
            "maxSecurityGroups": -1,
            "totalFloatingIpsUsed": 0,
            "totalInstancesUsed": 3,
            "totalSecurityGroupsUsed": 0,
            "maxServerMeta": 40,
            "maxTotalFloatingIps": -1,
            "maxTotalInstances": 200,
            "totalCoresUsed": 4,
            "maxTotalRAMSize": 256000
        }
    }
}

server_list_return = {
    "servers": [
        {
            "OS-EXT-STS:task_state": None,
            "addresses": {
                "public": [
                    {
                        "version": 4,
                        "addr": "104.130.28.32"
                    }, {
                        "version": 6,
                        "addr": "2001:4802:7803:104:be76:4eff:fe21:51b7"
                    }
                ],
                "private": [
                    {
                        "version": 4,
                        "addr": "10.176.205.68"
                    }
                ]
            },
            "flavor": {
                "id": "general1-1",
                "links": [
                    {
                        "href": (
                            "https://iad.servers.api.rackspacecloud.com"
                            "/766030/flavors/general1-1"
                        ),
                        "rel": "bookmark"
                    }
                ]
            },
            "id": "3290e50d-888f-4500-a934-16c10f3b8a10",
            "user_id": "284275",
            "OS-DCF:diskConfig": "MANUAL",
            "accessIPv4": "104.130.28.32",
            "accessIPv6": "2001:4802:7803:104:be76:4eff:fe21:51b7",
            "progress": 100,
            "OS-EXT-STS:power_state": 1,
            "config_drive": "",
            "status": "ACTIVE",
            "updated": "2016-01-12T15:16:37Z",
            "name": "test-server",
            "created": "2016-01-12T15:15:39Z",
            "tenant_id": "1234567",
            "metadata": {
                "build_config": "",
                "rax_service_level_automation": "Complete"
            }
        }
    ]
}

server_list_processed_return = [
    {
        'status': 'ACTIVE',
        'updated': '2016-01-12T15:16:37Z',
        'OS-EXT-STS:task_state': None,
        'user_id': '284275',
        'addresses': {
            'public': [
                {
                    'version': 4,
                    'addr': '104.130.28.32'
                }, {
                    'version': 6,
                    'addr': '2001:4802:7803:104:be76:4eff:fe21:51b7'
                }
            ],
            'private': [
                {
                    'version': 4,
                    'addr': '10.176.205.68'
                }
            ]
        },
        'created': '2016-01-12T15:15:39Z',
        'tenant_id': '1234567',
        'OS-DCF:diskConfig': 'MANUAL',
        'id': '3290e50d-888f-4500-a934-16c10f3b8a10',
        'accessIPv4': '104.130.28.32',
        'accessIPv6': '2001:4802:7803:104:be76:4eff:fe21:51b7',
        'config_drive': '',
        'progress': 100,
        'OS-EXT-STS:power_state': 1,
        'metadata': {
            'build_config': '',
            'rax_service_level_automation': 'Complete'
        },
        'flavor': {
            'id': 'general1-1',
            'links': [
                {
                    'href': (
                        'https://iad.servers.api.rackspacecloud.com'
                        '/766030/flavors/general1-1'
                    ),
                    'rel': 'bookmark'
                }
            ]
        },
        'name': 'test-server'
    }
]

network_list_return = {
    "networks": [
        {
            "status": "ACTIVE",
            "subnets": [
                "879ff280-6f17-4fd8-b684-19237d88fc45"
            ],
            "name": "test-network",
            "admin_state_up": True,
            "tenant_id": "1234567",
            "shared": False,
            "id": "e737483a-00d7-4517-afc3-bd1fbbbd4cd3"
        }
    ]
}

network_processed_list = [
    {
        'status': 'ACTIVE',
        'subnets': [
            '879ff280-6f17-4fd8-b684-19237d88fc45'
        ],
        'name': 'test-network',
        'admin_state_up': True,
        'tenant_id': '1234567',
        'shared': False,
        'id': 'e737483a-00d7-4517-afc3-bd1fbbbd4cd3'
    }
]

server_flavor_return = {
    "flavor": {
        "ram": 1024,
        "name": "1 GB General Purpose v1",
        "OS-FLV-WITH-EXT-SPECS:extra_specs": {
            "number_of_data_disks": "0",
            "class": "general1",
            "disk_io_index": "40",
            "policy_class": "general_flavor"
        },
        "vcpus": 1,
        "swap": "",
        "rxtx_factor": 200.0,
        "OS-FLV-EXT-DATA:ephemeral": 0,
        "disk": 20,
        "id": "general1-1"
    }
}

server_full_return = {
    'servers': {
        'values': {
            'Private Networks': 1,
            'Ram - MB': 1024,
            'Servers': 1
        },
        'limits': {
            'Private Networks': 10,
            'Ram - MB': 256000,
            'Servers': 200
        }
    }
}

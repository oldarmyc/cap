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


from celery.utils.log import get_task_logger
from future.utils import iteritems
from bson.objectid import ObjectId
from happymongo import HapPyMongo
from functools import reduce
from cap.models import Limit
from operator import getitem
from celery import Celery


import cap.config.celery as config
import requests
import json
import re


# Disable requests warnings from urllib3
requests.packages.urllib3.disable_warnings()


celery_app = Celery('cap')
logger = get_task_logger(__name__)
celery_app.config_from_object(config)
mongo, db = HapPyMongo(config)


def process_api_request(url, verb, data, headers, status=None):
    try:
        if data:
            response = getattr(requests, verb.lower())(
                url,
                headers=headers,
                data=json.dumps(data),
                verify=False
            )
        else:
            response = getattr(requests, verb.lower())(
                url,
                headers=headers,
                verify=False
            )

    except Exception as e:
        logger.error('An error occured executing the API call: %s' % e)

    try:
        if status and response:
            return response.status_code

        return json.loads(response.content)
    except Exception as e:
        logger.error('An error occured loading the content: %s' % e)
        return None


def generate_headers(token):
    temp_headers = {
        'X-Auth-Token': token,
        'Content-Type': 'application/json'
    }
    return temp_headers


def get_product_and_limits(db_name):
    temp_product = db.products.find_one({'db_name': db_name})
    temp_maps = {}
    limit_maps = db.limit_maps.find(
        {
            'product': db_name,
            'active': True
        }
    )
    if limit_maps.count() > 0:
        for limit in limit_maps:
            try:
                temp_maps[limit.get('uri')].append(Limit(limit))
            except:
                temp_maps[limit.get('uri')] = [Limit(limit)]

    return temp_product, temp_maps


def write_query_log(limits, log_id):
    db.query_logs.update(
        {
            '_id': ObjectId(log_id)
        }, {
            '$push': {
                'query_results': limits
            }
        }
    )


def generate_limit_url(product, uri, region, ddi):
    if region in ['uk', 'lon']:
        temp_url = product.get('uk_url')
    else:
        temp_url = product.get('us_url')

    return '%s%s' % (
        re.sub('(\{(region)\})', region, temp_url),
        re.sub('(\{(ddi)\})', ddi, uri)
    )


def generate_server_list(ddi, token, region):
    exit, all_servers, limit, marker = False, [], 100, None
    headers = generate_headers(token)
    while exit is False:
        if marker is None:
            url = (
                'https://%s.servers.api.rackspacecloud.com/v2/%s/'
                'servers/detail?limit=%d' % (
                    region.lower(),
                    ddi,
                    limit
                )
            )
        else:
            url = marker

        content = process_api_request(url, 'get', None, headers)
        if not content:
            break

        servers = content.get('servers')
        if len(servers) < limit:
            exit = True
        else:
            links = content.get('servers_links')[0]
            marker = links.get('href')

        all_servers += servers

    return all_servers


def generate_network_list(token, region):
    exit, all_networks, limit, marker = False, [], 100, None
    headers = generate_headers(token)
    while exit is False:
        if marker is None:
            url = (
                'https://%s.networks.api.rackspacecloud.com/v2.0/networks'
                '?limit=%d' % (
                    region.lower(),
                    limit
                )
            )
        else:
            url = marker

        content = process_api_request(url, 'get', None, headers)
        if not content:
            break

        networks = content.get('networks')
        if len(networks) < limit:
            exit = True
        else:
            links = content.get('network_links')[0]
            marker = links.get('href')

        all_networks += networks

    return all_networks


def generate_total_server_ram(servers, ddi, token, region):
    total_ram, flavors = 0, {}
    headers = generate_headers(token)
    for server in servers:
        flavor_info = server.get('flavor')
        flavor_id = flavor_info.get('id')
        if not flavors.get(flavor_id):
            flavor_url = (
                'https://%s.servers.api.rackspacecloud.com/v2/%s/'
                'flavors/%s' % (
                    region.lower(),
                    ddi,
                    flavor_id
                )
            )
            content = process_api_request(flavor_url, 'get', None, headers)
            if content:
                temp_flavor = content.get('flavor')
                temp_ram = int(temp_flavor.get('ram'))
                flavors[flavor_id] = temp_ram
                total_ram += temp_ram
        else:
            total_ram += flavors.get(flavor_id)

    return total_ram


def gather_all_load_balancers(token, ddi, region):
    exit, all_lbs, offset, paginate_limit = False, 0, 0, 100
    headers = generate_headers(token)
    while exit is False:
        url = (
            'https://%s.loadbalancers.api.rackspacecloud.com/v1.0/%s/'
            'loadbalancers?offset=%d&limit=%d' % (
                region.lower(),
                ddi,
                offset,
                paginate_limit
            )
        )
        content = process_api_request(url, 'get', None, headers)
        if not content:
            break

        lbs = content.get('loadBalancers')
        if len(lbs) < paginate_limit:
            exit = True
        else:
            offset += paginate_limit

        all_lbs += len(lbs)

    return all_lbs


def gather_autoscale_groups(ddi, token, region):
    all_groups = []
    headers = generate_headers(token)
    url = (
        'https://%s.autoscale.api.rackspacecloud.com/v1.0/%s/'
        'groups' % (
            region.lower(),
            ddi
        )
    )
    content = process_api_request(url, 'get', None, headers)
    if content:
        all_groups = content.get('groups')

    return len(all_groups)


def gather_dns_domains(ddi, token):
    all_domains = 0
    headers = generate_headers(token)
    url = 'https://dns.api.rackspacecloud.com/v1.0/%s/domains?limit=1' % (
        ddi
    )
    content = process_api_request(url, 'get', None, headers)
    if content:
        all_domains = content.get('totalEntries')

    return all_domains


def check_authorized(ddi, token):
    headers = generate_headers(token)
    url = 'https://identity.api.rackspacecloud.com/v2.0/tokens/%s' % token
    status_code = process_api_request(url, 'get', None, headers, True)
    if status_code == 200:
        return True

    return False


def gather_limits(token, ddi, region, product):
    limits = {}
    headers = generate_headers(token)
    product, limit_maps = get_product_and_limits(product)
    for uri, limit in iteritems(limit_maps):
        limit_url = generate_limit_url(product, uri, region, ddi)
        limit_result = process_api_request(limit_url, 'GET', None, headers)
        if not limit_result:
            break

        for item in limit:
            absolute_limits = reduce(
                getitem,
                item.absolute_path.split('.'),
                limit_result
            )
            if item.absolute_type == 'dict':
                try:
                    limits[product.get('db_name')]['limits'][item.title] = (
                        absolute_limits.get(item.limit_key)
                    )
                    if item.value_key:
                        limits[product.get('db_name')]['values'][
                            item.title
                        ] = absolute_limits.get(item.value_key)
                except:
                    limits[product.get('db_name')] = {}
                    limits[product.get('db_name')]['limits'] = {}
                    limits[product.get('db_name')]['values'] = {}
                    limits[product.get('db_name')]['limits'][item.title] = (
                        absolute_limits.get(item.limit_key)
                    )
                    if item.value_key:
                        limits[product.get('db_name')]['values'][
                            item.title
                        ] = absolute_limits.get(item.value_key)

            elif item.absolute_type == 'list':
                for temp in absolute_limits:
                    if temp.get('name') == item.limit_key:
                        try:
                            limits[product.get('db_name')]['limits'][
                                item.title
                            ] = temp.get('value')
                            # Here for a place holder in case it is needed
                            # if item.value_key:
                            #     limits[product.get('db_name')]['values'][
                            #         item.title
                            #     ] = absolute_limits.get(item.value_key)
                        except:
                            limits[product.get('db_name')] = {}
                            limits[product.get('db_name')]['limits'] = {}
                            limits[product.get('db_name')]['limits'][
                                item.title
                            ] = temp.get('value')
                            # Here for a place holder in case it is needed
                            # limits[product.get('db_name')]['values'] = {}
                            # if item.value_key:
                            #     limits[product.get('db_name')]['values'][
                            #         item.title
                            #     ] = temp.get('total', 0)
                        break

    return limits


@celery_app.task
def servers(token, ddi, region, product, log_id):
    results = gather_limits(token, ddi, region, product)
    total_servers = generate_server_list(ddi, token, region)
    total_networks = generate_network_list(token, region)
    total_ram = generate_total_server_ram(total_servers, ddi, token, region)
    results[product]['values']['Servers'] = len(total_servers)
    results[product]['values']['Private Networks'] = len(total_networks)
    results[product]['values']['Ram - MB'] = total_ram

    if len(results) > 0:
        write_query_log(results, log_id)

    return results


@celery_app.task
def load_balancers(token, ddi, region, product, log_id):
    results = gather_limits(token, ddi, region, product)
    total_lbs = gather_all_load_balancers(token, ddi, region)
    results['load_balancers']['values'] = {}
    results['load_balancers']['values']['Total Load Balancers'] = total_lbs

    if len(results) > 0:
        write_query_log(results, log_id)

    return results


@celery_app.task
def cbs(token, ddi, region, product, log_id):
    results = gather_limits(token, ddi, region, product)
    if len(results) > 0:
        write_query_log(results, log_id)

    return results


@celery_app.task
def big_data(token, ddi, region, product, log_id):
    results = gather_limits(token, ddi, region, product)
    temp_limits = results[product]['limits']
    for limit_title, value in iteritems(results[product]['values']):
        used = temp_limits.get(limit_title) - value
        results[product]['values'][limit_title] = used

    if len(results) > 0:
        write_query_log(results, log_id)

    return results


@celery_app.task
def autoscale(token, ddi, region, product, log_id):
    results = gather_limits(token, ddi, region, product)
    total_groups = gather_autoscale_groups(ddi, token, region)
    results['autoscale']['values']['Max Groups'] = total_groups

    if len(results) > 0:
        write_query_log(results, log_id)

    return results


@celery_app.task
def dns(token, ddi, region, product, log_id):
    results = gather_limits(token, ddi, region, product)
    total_domains = gather_dns_domains(ddi, token)
    results['dns']['values']['Domains'] = total_domains

    if len(results) > 0:
        write_query_log(results, log_id)

    return results


@celery_app.task
def check_auth_token(ddi, token):
    return check_authorized(ddi, token)


@celery_app.task
def check_tasks(task_id):
    return celery_app.AsyncResult(task_id)

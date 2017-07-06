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


from fixtures import test_product
from cap import setup_application
from datetime import datetime
from uuid import uuid4


import unittest
import uuid
import json
import mock
import cap
import re


class CapCeleryTests(unittest.TestCase):
    def setUp(self):
        self.app, self.db = setup_application.create_app('True')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.client.get('/')

        self.tasks = cap.tasks
        if not re.search('_test', self.tasks.config.MONGO_DATABASE):
            self.tasks.config.MONGO_DATABASE = (
                '%s_test' % self.tasks.config.MONGO_DATABASE
            )

        self.tasks.config.BROKER_URL = 'memory://'
        self.tasks.config.CELERY_RESULT_BACKEND = 'cache'
        self.tasks.config.CELERY_CACHE_BACKEND = 'memory'
        self.tasks.db = self.db

        self.db.products.remove({})
        self.db.limit_maps.remove({})

    def tearDown(self):
        collections = [
            'settings',
            'products',
            'managers',
            'sessions',
            'limit_maps',
            'query_logs'
        ]
        for c in collections:
            getattr(self.db, c).remove({})

    def setup_user_login(self, session):
        session['username'] = 'skeletor'
        session['csrf_token'] = uuid4().hex
        session['role'] = 'logged_in'
        session['email'] = 'skeletor@res.rackspace.com'
        session['_permanent'] = True
        session['name'] = 'Skeletor'
        session['token'] = uuid4().hex

    def setup_manager_login(self, session):
        session['username'] = 'he-man'
        session['csrf_token'] = uuid4().hex
        session['role'] = 'managers'
        session['email'] = 'manager@res.rackspace.com'
        session['_permanent'] = True
        session['name'] = 'Default Manager'
        session['token'] = uuid4().hex

    def setup_useable_member(self, disabled=None):
        data = {
            'username': 'skeletor',
            'active': True,
            'name': 'Test Admin',
            'email': 'test@test.com'
        }
        if disabled:
            data['status'] = False

        self.db.settings.update(
            {}, {
                '$push': {
                    'exemptions': data
                }
            }
        )

    def setup_usable_log(self, product):
        data = {
            'ddi': '1234567',
            'region': 'dfw',
            'queried': [product],
            'query_results': [],
            'queried_at': datetime.now(),
            'queried_by': 'skeletor'
        }
        return self.db.query_logs.insert(data)

    def setup_admin_login(self, session):
        session['username'] = 'bob.richards'
        session['csrf_token'] = uuid4().hex
        session['role'] = 'administrators'
        session['email'] = 'admin@res.rackspace.com'
        session['_permanent'] = True
        session['name'] = 'Default Admin'
        session['token'] = uuid4().hex

    def setup_useable_log(self):
        data = {
            "queried": ["servers"],
            "queried_by": "bob.richards",
            "region": "dfw",
            "ddi": "123456",
            "queried_at": datetime.now()
        }
        self.db.query_logs.insert(data)

    """ Tasks Tests """

    def test_celery_check_token(self):
        cloud_return = {
            'users': [
                {
                    'RAX-AUTH:domainId': '123456',
                    'username': 'bob.richards',
                    'enabled': True,
                    'email': 'bob.richards@rackspace.com',
                    'RAX-AUTH:defaultRegion': 'ORD',
                    'RAX-AUTH:multiFactorEnabled': False,
                    'id': '11111111'
                }
            ]
        }
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(cloud_return)
                    patched_get.return_value.status_code = 200
                    task = self.tasks.check_auth_token(
                        '123456',
                        uuid.uuid4().hex,
                    )

        assert task is True, 'Incorrect status returned with check'

    def test_celery_check_token_error(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    error = patched_get.side_effect = ValueError
                    patched_get.return_value = error
                    task = self.tasks.check_auth_token(
                        '123456',
                        uuid.uuid4().hex,
                    )

        assert task is False, 'Incorrect status returned with check'

    def test_process_data_json_success(self):
        cloud_return = {'servers': []}
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(cloud_return)
                    patched_get.return_value.status_code = 200
                    task = self.tasks.process_api_request(
                        'https://dfw.servers.api.rackspacecloud.com'
                        '/v2/123456/servers/detail',
                        'GET',
                        {'test': 'test'},
                        {'Content-Type': 'application/json'}
                    )

        assert cloud_return == task, 'Return value did not match'

    """ DNS """

    def test_dns_success(self):
        self.db.products.insert(test_product.dns)
        self.db.limit_maps.insert(test_product.dns_limit)
        log_id = self.setup_usable_log('dns')
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.dns_limit_return
                    )
                    patched_get.return_value.status_code = 200
                    with mock.patch('cap.tasks.gather_dns_domains') as count:
                        count.return_value = 1
                        return_value = self.tasks.dns(
                            uuid.uuid4().hex,
                            '123467',
                            'DFW',
                            'dns',
                            log_id
                        )
        assert return_value == test_product.dns_full_return, (
            'Returned value did not match expected value'
        )
        log = self.db.query_logs.find_one()
        assert log.get('query_results')[0] == test_product.dns_full_return, (
            'Logged results do not match expected return'
        )

    def test_gather_dns_domain_list(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.dns_list_return
                    )
                    patched_get.return_value.status_code = 200
                    return_value = self.tasks.gather_dns_domains(
                        '123467',
                        uuid.uuid4().hex,
                    )

        assert return_value == 1, 'Did not get expected count return on list'

    """ Autoscale """

    def test_autoscale_success(self):
        self.db.products.insert(test_product.autoscale)
        self.db.limit_maps.insert(test_product.autoscale_limit)
        log_id = self.setup_usable_log('autoscale')
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.autoscale_limit_return
                    )
                    patched_get.return_value.status_code = 200
                    with mock.patch('cap.tasks.gather_autoscale_groups') as c:
                        c.return_value = 1
                        return_value = self.tasks.autoscale(
                            uuid.uuid4().hex,
                            '123467',
                            'DFW',
                            'autoscale',
                            log_id
                        )

        print(return_value)
        print(test_product.autoscale_full_return)

        self.assertEqual(
            return_value,
            test_product.autoscale_full_return,
            'Returned value did not match expected value'
        )
        log = self.db.query_logs.find_one()
        self.assertEqual(
            log.get('query_results')[0],
            test_product.autoscale_full_return,
            'Logged results do not match expected return'
        )

    def test_gather_autoscale_groups(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.autoscale_list_return
                    )
                    patched_get.return_value.status_code = 200
                    return_value = self.tasks.gather_autoscale_groups(
                        '123467',
                        uuid.uuid4().hex,
                        'DFW'
                    )

        assert return_value == 1, 'Did not get expected count return on list'

    """ Big Data """

    def test_big_data_success(self):
        self.db.products.insert(test_product.big_data)
        self.db.limit_maps.insert(test_product.big_data_limit)
        log_id = self.setup_usable_log('big_data')
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.big_data_limit_return
                    )
                    patched_get.return_value.status_code = 200
                    return_value = self.tasks.big_data(
                        uuid.uuid4().hex,
                        '123467',
                        'DFW',
                        'big_data',
                        log_id
                    )

        assert return_value == test_product.big_data_full_return, (
            'Returned value did not match expected value'
        )
        log = self.db.query_logs.find_one()
        self.assertEqual(
            log.get('query_results')[0],
            test_product.big_data_full_return,
            'Logged results do not match expected return'
        )

    """ CBS """

    def test_cbs_success(self):
        self.db.products.insert(test_product.cbs)
        self.db.limit_maps.insert(test_product.cbs_limit)
        log_id = self.setup_usable_log('cbs')
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.cbs_limit_return
                    )
                    patched_get.return_value.status_code = 200
                    return_value = self.tasks.big_data(
                        uuid.uuid4().hex,
                        '123467',
                        'lon',
                        'cbs',
                        log_id
                    )

        assert return_value == test_product.cbs_full_return, (
            'Returned value did not match expected value'
        )
        log = self.db.query_logs.find_one()
        assert log.get('query_results')[0] == test_product.cbs_full_return, (
            'Logged results do not match expected return'
        )

    """ LBs """

    def test_load_balancers_success(self):
        self.db.products.insert(test_product.clb)
        self.db.limit_maps.insert(test_product.clb_limit)
        log_id = self.setup_usable_log('load_balancers')
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.clb_limit_return
                    )
                    patched_get.return_value.status_code = 200
                    with mock.patch(
                        'cap.tasks.gather_all_load_balancers'
                    ) as count:
                        count.return_value = 1
                        return_value = self.tasks.load_balancers(
                            uuid.uuid4().hex,
                            '123467',
                            'DFW',
                            'load_balancers',
                            log_id
                        )

        assert return_value == test_product.clb_full_return, (
            'Returned value did not match expected value'
        )
        log = self.db.query_logs.find_one()
        assert log.get('query_results')[0] == test_product.clb_full_return, (
            'Logged results do not match expected return'
        )

    def test_gather_all_load_balancers(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.clb_list_return
                    )
                    patched_get.return_value.status_code = 200
                    return_value = self.tasks.gather_all_load_balancers(
                        uuid.uuid4().hex,
                        '123467',
                        'DFW'
                    )

        assert return_value == 1, 'Did not get expected count return on list'

    """ Servers """

    def test_servers_success(self):
        self.db.products.insert(test_product.server)
        self.db.limit_maps.insert(test_product.server_limit)
        log_id = self.setup_usable_log('server')
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.server_limit_return
                    )
                    patched_get.return_value.status_code = 200
                    with mock.patch(
                        'cap.tasks.generate_server_list'
                    ) as server_list:
                        server_list.return_value = (
                            test_product.server_list_return
                        )
                        with mock.patch(
                            'cap.tasks.generate_network_list'
                        ) as network_list:
                            network_list.return_value = (
                                test_product.network_processed_list
                            )
                            with mock.patch(
                                'cap.tasks.generate_total_server_ram'
                            ) as ram:
                                ram.return_value = 1024
                                return_value = self.tasks.servers(
                                    uuid.uuid4().hex,
                                    '123467',
                                    'DFW',
                                    'servers',
                                    log_id
                                )

        assert return_value == test_product.server_full_return, (
            'Returned value did not match expected value'
        )
        log = self.db.query_logs.find_one()
        self.assertEqual(
            log.get('query_results')[0],
            test_product.server_full_return,
            'Logged results do not match expected return'
        )

    def test_generate_server_list(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.server_list_return
                    )
                    patched_get.return_value.status_code = 200
                    return_value = self.tasks.generate_server_list(
                        '123467',
                        uuid.uuid4().hex,
                        'DFW'
                    )

        assert return_value == test_product.server_list_processed_return, (
            'Did not get expected count return on list'
        )

    def test_generate_network_list(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.network_list_return
                    )
                    patched_get.return_value.status_code = 200
                    return_value = self.tasks.generate_network_list(
                        uuid.uuid4().hex,
                        'DFW'
                    )

        assert return_value == test_product.network_processed_list, (
            'Did not get expected count return on list'
        )

    def test_generate_total_server_ram(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('requests.get') as patched_get:
                    patched_get.return_value.content = json.dumps(
                        test_product.server_flavor_return
                    )
                    patched_get.return_value.status_code = 200
                    return_value = self.tasks.generate_total_server_ram(
                        test_product.server_list_processed_return,
                        '123467',
                        uuid.uuid4().hex,
                        'DFW'
                    )

        assert return_value == 1024, (
            'Did not get expected count return on list'
        )

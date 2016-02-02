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


from fixtures.test_product import sample_log, sample_auth_failure
from cap.setup_application import create_app
from cap.config import config
from uuid import uuid4


# Needed for Python 2 & 3
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse


import unittest
import json
import mock
import uuid
import re


class SetState:
    def __init__(self, state, info):
        self.state = state
        self.info = info

    def info(self):
        return self.info

    def state(self):
        return self.state


class UITests(unittest.TestCase):
    def setUp(self):
        check_db = re.search('_test', config.MONGO_DATABASE)
        if not check_db:
            test_db = '%s_test' % config.MONGO_DATABASE
        else:
            test_db = config.MONGO_DATABASE

        self.cap, self.db = create_app(test_db)
        self.app = self.cap.test_client()
        self.app.get('/')

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

    def setup_user_login(self, sess):
        sess['username'] = 'skeletor'
        sess['csrf_token'] = 'csrf_token'
        sess['role'] = 'logged_in'
        sess['_permanent'] = True
        sess['ddi'] = '123456'
        sess['cloud_token'] = uuid4().hex

    def setup_usable_product(self):
        self.db.products.insert(
            {
                "title": "Test",
                "us_url": "http://us.test.com",
                "uk_url": "http://uk.test.com",
                "active": True,
                "db_name": "test",
                "require_region": True,
                "doc_url": "http://doc.test.com",
                "pitchfork_url": "https://pitchfork/url",
                "limit_maps": []
            }
        )

    def setup_usable_limit(self, deactivate=None):
        data = {
            "product": "test",
            "title": "Test",
            "uri": "/limits",
            "slug": "test",
            "active": True,
            "absolute_path": "test/path",
            "absolute_type": "list",
            "limit_key": "test_limit"
        }
        if deactivate:
            data['active'] = False

        self.db.limit_maps.insert(data)

    def setup_admin_login(self, session):
        session['username'] = 'bob.richards'
        session['csrf_token'] = uuid4().hex
        session['role'] = 'administrators'
        session['email'] = 'admin@res.rackspace.com'
        session['_permanent'] = True
        session['name'] = 'Default Admin'
        session['token'] = uuid4().hex

    def retrieve_csrf_token(self, data):
        temp = re.search('id="csrf_token"(.+?)>', data.decode('utf-8'))
        if temp:
            token = re.search('value="(.+?)"', temp.group(1))
            if token:
                return token.group(1)
        return 'UNK'

    """ Index and Auth Tests """

    def test_ui_index(self):
        response = self.app.get('/')
        assert response.status_code == 200, (
            'Invalid response code %s, expected 200' % response.status_code
        )
        self.assertIn(
            'Cap',
            response.data.decode('utf-8'),
            'Could not find application title in index'
        )

    def test_ui_all_perms(self):
        self.db.settings.update(
            {
                'menu.db_name': 'general_settings'
            }, {
                '$set': {
                    'menu.$.permissions': 'all'
                }
            }
        )
        self.db.settings.update(
            {
                'roles.slug': 'all'
            }, {
                '$set': {
                    'roles.$.perms': ['/admin/general/']
                }
            }
        )
        response = self.app.get('/admin/login')
        self.assertEquals(
            response.status_code,
            200,
            'Invalid response code %s, expected 200' % response.status_code
        )

    def test_ui_login_form_validation(self):
        with self.app as c:
            response = c.get('/admin/login')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'username': 'skeletor',
                'password': ''
            }
            response = c.post('/admin/login', data=data)

        self.assertIn(
            'Form validation error, please check the form and try again',
            response.data.decode('utf-8'),
            'Expected form validation error and did not get one'
        )

    def test_ui_login_get(self):
        response = self.app.get('/admin/login')
        self.assertEquals(
            response.status_code,
            200,
            'Invalid response code %s, expected 200' % response.status_code
        )

    def test_ui_logout(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/admin/logout/')

        set_cookie = response.headers.get('Set-Cookie')
        self.assertIn('session=;', set_cookie, 'Session not correctly unset')

    def test_ui_no_session(self):
        response = self.app.get('/admin/general/')
        self.assertEqual(
            response.status_code,
            302,
            'Invalid response code %s' % response.status_code
        )
        location = response.headers.get('Location')
        o = urlparse(location)
        self.assertEqual(
            o.path,
            '/admin/login',
            'Invalid redirect location %s' % o.path
        )

    """ Query tests """

    def test_ui_query_perms(self):
        response = self.app.get('/query/')
        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = response.headers.get('Location')
        o = urlparse(location)
        self.assertEqual(
            o.path,
            '/admin/login',
            'Invalid redirect location %s, expected "/admin/login"' % o.path
        )

    def test_manage_regions_admin_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/query/')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Query Limits',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    def test_manage_regions_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/query/')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Query Limits',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    def test_manage_regions_user_perms_with_product(self):
        self.setup_usable_product()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/query/')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Query Limits',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )
        self.assertIn(
            'id="test"',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    """ Query Posts """

    def test_query_post_success(self):
        task_id = uuid.uuid4().hex
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/query/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'ddi': '123456',
                'region': 'dfw',
                'token': uuid.uuid4().hex,
                'dns': 'y'
            }
            with mock.patch(
                'cap.tasks.config.CELERY_ALWAYS_EAGER',
                True,
                create=True
            ):
                with mock.patch('cap.tasks.check_auth_token') as auth:
                    auth.return_value = True
                    with mock.patch('cap.tasks.dns') as limit:
                        limit.return_value = task_id
                        response = c.post(
                            '/query/',
                            data=json.dumps(data),
                            content_type='application/json'
                        )

        try:
            result = json.loads(response.data.decode('utf-8'))
        except:
            assert False, 'Could not load JSON from returned results'

        try:
            tasks = result.get('tasks')
        except:
            assert False, 'Not able to retrieve tasks from results'

        self.assertEquals(
            1,
            len(tasks),
            'Incorrect length on tasks list'
        )
        assert tasks[0].get('dns'), 'Could not find test product in return'
        log_entry = self.db.query_logs.find_one()
        assert log_entry, 'Log entry not found'
        del log_entry['_id']
        del log_entry['queried_at']
        self.assertEquals(
            sample_log,
            log_entry,
            'Log does not match expected value'
        )

    def test_query_post_bad_auth(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/query/')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'ddi': '123456',
                'region': 'dfw',
                'token': uuid.uuid4().hex,
                'servers': 'y'
            }
            with mock.patch('cap.tasks.check_auth_token') as auth:
                auth.return_value = False
                result = c.post(
                    '/query/',
                    data=json.dumps(data),
                    content_type='application/json'
                )

        returned = json.loads(result.data.decode('utf-8'))
        log_entry = self.db.query_logs.find_one()
        self.assertEquals(
            returned,
            sample_auth_failure,
            'Invalid response received from successfull query submit'
        )
        self.assertEquals(
            result.status_code,
            401,
            'Invalid status code received on bad auth'
        )
        assert log_entry is None, 'Log entry found when should not have been'

    """ Task Status and returns w/ template functions """

    def test_task_status_pending(self):
        state = SetState('PENDING', None)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('cap.tasks.check_tasks') as check_task:
                check_task.return_value = state
                response = c.get(
                    '/query/status/%s' % uuid4().hex
                )

        results = json.loads(response.data.decode('utf-8'))
        self.assertEquals(
            results,
            {'state': 'PENDING'},
            'Pending check did not return the correct data object'
        )

    def test_task_status_failure(self):
        state = SetState('FAILURE', 'Test Error Message')
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('cap.tasks.check_tasks') as check_task:
                check_task.return_value = state
                response = c.get(
                    '/query/status/%s' % uuid4().hex
                )

        results = json.loads(response.data.decode('utf-8'))
        self.assertEquals(
            results,
            {'state': 'FAILURE', 'status': 'Test Error Message'},
            'Failed check did not return the correct data object'
        )

    def test_task_status_success_warning(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        success_data = {
            'test': {'limits': {'Test': 20}, 'values': {'Test': 15}}
        }
        state = SetState('SUCCESS', success_data)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('cap.tasks.check_tasks') as check_task:
                check_task.return_value = state
                response = c.get(
                    '/query/status/%s' % uuid4().hex
                )

        self.assertIn(
            'limit-alert-text-warning',
            response.data.decode('utf-8'),
            'Could not find text warning classes'
        )
        self.assertIn(
            'http://doc.test.com',
            response.data.decode('utf-8'),
            'Could not find correct product URL in return'
        )

    def test_task_status_success_danger(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        success_data = {
            'test': {'limits': {'Test': 20}, 'values': {'Test': 19}}
        }
        state = SetState('SUCCESS', success_data)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('cap.tasks.check_tasks') as check_task:
                check_task.return_value = state
                response = c.get(
                    '/query/status/%s' % uuid4().hex
                )

        self.assertIn(
            'limit-alert-text-danger',
            response.data.decode('utf-8'),
            'Could not find text danger classes'
        )

    def test_task_status_success_clear(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        success_data = {
            'test': {'limits': {'Test': 20}, 'values': {'Test': 1}}
        }
        state = SetState('SUCCESS', success_data)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('cap.tasks.check_tasks') as check_task:
                check_task.return_value = state
                response = c.get(
                    '/query/status/%s' % uuid4().hex
                )

        self.assertIn(
            'text-success',
            response.data.decode('utf-8'),
            'Could not find text success classes'
        )

    def test_task_status_success_no_product(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        success_data = {
            'bad_product': {'limits': {'Test': 20}, 'values': {'Test': 1}}
        }
        state = SetState('SUCCESS', success_data)
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            with mock.patch('cap.tasks.check_tasks') as check_task:
                check_task.return_value = state
                response = c.get(
                    '/query/status/%s' % uuid4().hex
                )

        self.assertNotIn(
            '<table',
            response.data.decode('utf-8'),
            'Found table code when there should be empty return'
        )

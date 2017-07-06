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
from cap.config import config
from uuid import uuid4


# Needed for Python 2 & 3
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse


import unittest
import re


class CapManageTests(unittest.TestCase):
    def setUp(self):
        check_db = re.search('_test', config.MONGO_DATABASE)
        if not check_db:
            test_db = '%s_test' % config.MONGO_DATABASE
        else:
            test_db = config.MONGO_DATABASE

        self.cap, self.db = setup_application.create_app(test_db)
        self.app = self.cap.test_client()
        self.app.get('/')

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

    def setup_admin_login(self, session):
        session['username'] = 'bob.richards'
        session['csrf_token'] = uuid4().hex
        session['role'] = 'administrators'
        session['email'] = 'admin@res.rackspace.com'
        session['_permanent'] = True
        session['name'] = 'Default Admin'
        session['token'] = uuid4().hex

    def setup_useable_admin(self):
        self.db.settings.update(
            {}, {
                '$push': {
                    'administrators': {
                        'admin_sso': 'test1234',
                        'admin_name': 'Test Admin',
                        'admin_email': 'test@test.com'
                    }
                }
            }
        )

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

    def retrieve_csrf_token(self, data):
        temp = re.search(b'id="csrf_token"(.+?)>', data)
        if temp:
            token = re.search(b'value="(.+?)"', temp.group(1))
            if token:
                return token.group(1).decode('utf-8')
        return 'UNK'

    """ Regions Management - Perms Tests """

    def test_manage_regions_admin_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage Regions',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    def test_manage_regions_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            result = c.get('/manage/regions')

        assert result._status_code == 302, (
            'Invalid response code %s' % result._status_code
        )
        request_path = urlparse(result.headers.get('Location')).path
        self.assertEqual(
            request_path,
            '/',
            'Invalid redirect location %s, expected "/"' % request_path
        )

    """ Regions Management - Functional Tests """

    def test_manage_regions_add_no_defaults(self):
        self.db.settings.update({}, {'$unset': {'regions': 1}})
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Region successfully added to system',
            response.data.decode('utf-8'),
            'Incorrect flash message after add'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        self.assertEquals(
            len(regions),
            1,
            'Incorrect after empty add of region'
        )
        assert isinstance(regions, list), 'Regions data type is incorrect'
        found_add = self.db.settings.find_one(
            {
                'regions.name': 'Test'
            }
        )
        assert found_add, 'Region not found after add'

    def test_manage_regions_add(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Region successfully added to system',
            response.data.decode('utf-8'),
            'Incorrect flash message after add'
        )
        found_add = self.db.settings.find_one(
            {
                'regions.name': 'Test'
            }
        )
        assert found_add, 'Region not found after add'

    def test_manage_regions_add_no_dcs(self):
        self.db.regions.update({}, {'$unset': {'regions': 1}})
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Region successfully added to system',
            response.data.decode('utf-8'),
            'Incorrect flash message after add'
        )
        found_add = self.db.settings.find_one(
            {
                'regions.name': 'Test'
            }
        )
        assert found_add, 'Region not found after add'

    def test_manage_regions_add_dupe(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'name': 'Dallas',
                'abbreviation': 'DFW'
            }

            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Duplicate name',
            response.data.decode('utf-8'),
            'Incorrect error message after add duplicate'
        )
        self.assertIn(
            'Duplicate abbreviation',
            response.data.decode('utf-8'),
            'Incorrect error message after add duplicate'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        count = 0
        for region in regions:
            if region.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after dupe add found %d instead of 1' % count
        )

    def test_manage_regions_add_bad_data(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/regions')
            data = {
                'name': 'Test',
                'abbreviation': 'TEST'
            }
            response = c.post(
                '/manage/regions',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            (
                'There was a form validation error, please check '
                'the required values and try again.'
            ),
            response.data.decode('utf-8'),
            'Incorrect flash message after add bad data'
        )

    def test_manage_regions_remove(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/delete/DFW',
                follow_redirects=True
            )

        self.assertIn(
            'Dfw was deleted successfully',
            response.data.decode('utf-8'),
            'Incorrect flash message after remove'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        count = 0
        for region in regions:
            if region.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            0,
            'Incorrect count after remove, found %d instead of 0' % count
        )

    def test_bad_key_for_actions(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/BAD_KEY/delete/DFW',
                follow_redirects=True
            )

        self.assertIn(
            'Invalid data key given so no action taken',
            response.data.decode('utf-8'),
            'Incorrect flash message after bad key'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        count = 0
        for region in regions:
            if region.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after bad key, found %d instead of 1' % count
        )

    def test_bad_action_for_actions(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/BAD_ACTION/DFW',
                follow_redirects=True
            )

        self.assertIn(
            'Invalid action given so no action taken',
            response.data.decode('utf-8'),
            'Incorrect flash message after bad action'
        )
        settings = self.db.settings.find_one()
        regions = settings.get('regions')
        count = 0
        for region in regions:
            if region.get('name') == 'Dallas':
                count += 1

        self.assertEquals(
            count,
            1,
            'Incorrect count after bad key, found %d instead of 1' % count
        )

    def test_bad_dat_element_for_actions(self):
        before_settings = self.db.settings.find_one()
        before_regions = before_settings.get('regions')
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/regions/delete/BAD_DATA',
                follow_redirects=True
            )

        self.assertIn(
            'Bad_Data was not found so no action taken',
            response.data.decode('utf-8'),
            'Incorrect flash message after bad data'
        )
        after_settings = self.db.settings.find_one()
        after_regions = after_settings.get('regions')
        self.assertEquals(
            after_regions,
            before_regions,
            'Incorrect count after bad key on delete'
        )

    """ Product Management - Perms Tests """

    def test_manage_product_admin_perms(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/product/test')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Test Manage Settings',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    def test_manage_product_admin_perms_no_settings(self):
        self.db.api_settings.remove()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/product/servers')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Servers Manage Settings',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    def test_manage_product_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/manage/product/servers')

        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = response.headers.get('Location')
        o = urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )

    def test_manage_all_products_admin_perms(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/products')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'All Products',
            response.data.decode('utf-8'),
            'Did not find correct title on page'
        )
        self.assertIn(
            '/limits',
            response.data.decode('utf-8'),
            'Did not find correct limit URI on page'
        )

    def test_manage_all_products_user_perms(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/manage/products')

        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = response.headers.get('Location')
        o = urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )

    def test_manage_all_products_none(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/products')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'All Products',
            response.data.decode('utf-8'),
            'Did not find correct title on page'
        )
        self.assertIn(
            'No products have been setup in the system',
            response.data.decode('utf-8'),
            'Did not find correct warning with no products'
        )

    def test_manage_all_products_no_limits(self):
        self.setup_usable_product()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/products')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'All Products',
            response.data.decode('utf-8'),
            'Did not find correct title on page'
        )
        self.assertIn(
            'No limit mappings have been setup for this product',
            response.data.decode('utf-8'),
            'Did not find correct warning with no limits'
        )

    """ Product Management - Functional Tests """

    def test_manage_product_add_initial(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/product/servers')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Test',
                'us_url': 'http://us.test.com',
                'uk_url': 'http://uk.test.com',
                'doc_url': 'http://doc.test.com',
                "pitchfork_url": "https://pitchfork/url",
                'require_region': True,
                'active': True
            }
            response = c.post(
                '/manage/product/servers',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Product was successfully added',
            response.data.decode('utf-8'),
            'Incorrect flash message after add product'
        )
        product = self.db.products.find_one()
        assert product, 'Could not find new product'
        del product['_id']
        self.assertEquals(
            product,
            test_product.sample_product,
            'Product added does not match expected product'
        )

    def test_manage_product_update(self):
        self.setup_usable_product()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/product/test')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'Test       Edit',
                'app_url': '/test',
                'us_url': 'http://us.test.com',
                'uk_url': 'http://uk.test.com',
                'doc_url': 'http://doc.test.com',
                "pitchfork_url": "https://pitchfork/url",
                'limit_uri': '/limits',
                'require_region': False
            }
            response = c.post(
                '/manage/product/test',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Product was successfully updated',
            response.data.decode('utf-8'),
            'Incorrect flash message after data update'
        )
        product = self.db.products.find_one()
        assert not product.get('active'), 'Status was not changed correctly'
        self.assertEquals(
            product.get('title'),
            'Test Edit',
            'Name was not formatted correctly'
        )
        self.assertEquals(
            product.get('db_name'),
            'test',
            'DB Name was changed and should not have been'
        )

    def test_manage_product_manage_add_bad_data(self):
        self.db.products.remove({})
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'title': 'Test',
                'app_url': '/test',
                'us_url': 'http://us.test.com',
                'uk_url': 'http://us.test.com',
                'doc_url': 'http://doc.test.com',
                'require_dc': True,
                'active': True
            }
            response = c.post(
                '/manage/product/test',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form was not saved successfully',
            response.data.decode('utf-8'),
            'Incorrect flash message after add bad data'
        )
        product = self.db.products.find()
        self.assertEquals(
            product.count(),
            0,
            'Product added when should not have been'
        )

    """ Product Management - Perms Tests """

    def test_manage_limit_admin_perms(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/limits')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage Limits',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    def test_manage_limit_admin_perms_no_product(self):
        self.setup_usable_limit()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/limits')

        assert response._status_code == 200, (
            'Invalid response code %s' % response._status_code
        )
        self.assertIn(
            'Manage Limits',
            response.data.decode('utf-8'),
            'Did not find correct HTML on page'
        )

    def test_manage_limit_user_perms(self):
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_user_login(sess)

            response = c.get('/manage/limits')

        assert response._status_code == 302, (
            'Invalid response code %s' % response._status_code
        )
        location = response.headers.get('Location')
        o = urlparse(location)
        self.assertEqual(
            o.path,
            '/',
            'Invalid redirect location %s, expected "/"' % o.path
        )

    """ Product Management - Functional Tests """

    def test_manage_limit_add_initial(self):
        self.setup_usable_product()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/limits')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'product': 'test',
                'title': 'Test',
                'uri': '/limits',
                "absolute_path": "test/path",
                "absolute_type": "list",
                "limit_key": "test_limit",
                "value_key": "test_value",
                'active': True
            }
            response = c.post(
                '/manage/limits',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Limit successfully added',
            response.data.decode('utf-8'),
            'Incorrect flash message after add limit'
        )
        limit = self.db.limit_maps.find_one()
        assert limit, 'Could not find new product'
        del limit['_id']
        self.assertEquals(
            limit,
            test_product.sample_limit,
            'Limit added does not match expected limit'
        )

    def test_manage_limit_update(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        limit = self.db.limit_maps.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/limits/%s' % limit.get('_id'))
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                "product":  "test",
                "title": "Test     Edit",
                "slug": "test",
                "uri": "/limits",
                "absolute_path": "test/path/edit",
                "absolute_type": "list",
                "value_key": "test_limit"
            }
            response = c.post(
                '/manage/limits/%s' % limit.get('_id'),
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Limit successfully updated',
            response.data.decode('utf-8'),
            'Incorrect flash message after data update'
        )
        limit = self.db.limit_maps.find_one()
        assert not limit.get('active'), 'Status was not changed correctly'
        self.assertEquals(
            limit.get('title'),
            'Test Edit',
            'Name was not formatted correctly'
        )
        self.assertEquals(
            limit.get('slug'),
            'test_edit',
            'Slug is not correct after title change'
        )

    def test_manage_limit_update_not_found(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        limit = self.db.limit_maps.find_one()
        self.db.limit_maps.remove({})
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/limits/%s' % limit.get('_id'))
            assert response._status_code == 302, (
                'Invalid response code %s' % response._status_code
            )
            response = c.get(
                '/manage/limits/%s' % limit.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'Could not find the specified limit',
            response.data.decode('utf-8'),
            'Incorrect flash message after not found limit'
        )

    def test_manage_limit_add_bad_token(self):
        self.db.products.remove({})
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            data = {
                'title': 'Test',
                'product': 'test',
                'title': 'Test',
                'path': 'test/path',
                'active': True
            }
            response = c.post(
                '/manage/product/test',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'Form was not saved successfully',
            response.data.decode('utf-8'),
            'Incorrect flash message after add bad data'
        )
        limit = self.db.limt_maps.find()
        self.assertEquals(
            limit.count(),
            0,
            'Limit added when should not have been'
        )

    def test_manage_limit_add_duplicate_limit(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        limit = self.db.limit_maps.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/limits')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': limit.get('title'),
                'product': 'test',
                'path': 'test/path/new',
                'active': True
            }
            response = c.post(
                '/manage/limits',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'There was a form validation error, '
            'please check the required values and try again.',
            response.data.decode('utf-8'),
            'Incorrect flash message after add bad data'
        )
        self.assertIn(
            'Duplicate limit',
            response.data.decode('utf-8'),
            'Incorrect error message after add duplicate limit'
        )
        limit = self.db.limit_maps.find()
        self.assertEquals(
            limit.count(),
            1,
            'Limit added when should not have been'
        )

    def test_manage_limit_add_duplicate_path(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        limit = self.db.limit_maps.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get('/manage/limits')
            token = self.retrieve_csrf_token(response.data)
            data = {
                'csrf_token': token,
                'title': 'New Test',
                'product': 'test',
                'uri': '/limits',
                "absolute_path": "test/path",
                "absolute_type": "list",
                "limit_key": "test_limit",
                "value_key": "test_value",
                'active': True
            }
            response = c.post(
                '/manage/limits',
                data=data,
                follow_redirects=True
            )

        self.assertIn(
            'There was a form validation error, '
            'please check the required values and try again.',
            response.data.decode('utf-8'),
            'Incorrect flash message after add duplicate data'
        )
        self.assertIn(
            'Duplicate URI with path and key',
            response.data.decode('utf-8'),
            'Incorrect error message after add duplicate path'
        )
        limit = self.db.limit_maps.find()
        self.assertEquals(
            limit.count(),
            1,
            'Limit added when should not have been'
        )

    def test_manage_limit_deactivate(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        limit = self.db.limit_maps.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/limits/deactivate/%s' % limit.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'was deactivated successfully',
            response.data.decode('utf-8'),
            'Incorrect flash message after deactivate'
        )
        limit = self.db.limit_maps.find_one()
        assert not limit.get('active'), 'Status was not changed correctly'

    def test_manage_limit_activate(self):
        self.setup_usable_product()
        self.setup_usable_limit(True)
        limit = self.db.limit_maps.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/limits/activate/%s' % limit.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'was activated successfully',
            response.data.decode('utf-8'),
            'Incorrect flash message after activate'
        )
        limit = self.db.limit_maps.find_one()
        assert limit.get('active'), 'Status was not changed correctly'

    def test_manage_limit_delete(self):
        self.setup_usable_product()
        self.setup_usable_limit()
        limit = self.db.limit_maps.find_one()
        with self.app as c:
            with c.session_transaction() as sess:
                self.setup_admin_login(sess)

            response = c.get(
                '/manage/limits/delete/%s' % limit.get('_id'),
                follow_redirects=True
            )

        self.assertIn(
            'was deleted successfully',
            response.data.decode('utf-8'),
            'Incorrect flash message after delete'
        )
        limit = self.db.limit_maps.find()
        self.assertEquals(
            limit.count(),
            0,
            'Incorrect count after delete'
        )

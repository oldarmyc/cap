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


from flask import (
    render_template, request, redirect, g, flash, url_for, jsonify
)
from flask.ext.cloudadmin.decorators import check_perms
from cap.models import Region, Product, Limit
from flask.ext.classy import FlaskView, route
from cap import forms, helper, tasks
from bson.objectid import ObjectId
from future.utils import iteritems


import pymongo
import copy


class BaseView(FlaskView):
    route_base = '/'

    def index(self):
        return render_template('index.html')


class QueryView(FlaskView):
    decorators = [check_perms(request)]
    route_base = '/query'

    def index(self):
        settings = g.db.settings.find_one()
        products = g.db.products.find({'active': True}).sort(
            'title', pymongo.ASCENDING
        )
        form = forms.generate_limits_form(products)
        return render_template(
            'query.html',
            form=form,
            regions=settings.get('regions')
        )

    def post(self):
        # Confirm token is good before proceeding
        products, task_ids = [], []
        ddi = request.json.get('ddi')
        token = request.json.get('token')
        region = request.json.get('region')
        if tasks.check_auth_token(ddi, token):
            # Store log entry of query and pass along the id of the record
            log_data = copy.copy(request.json)
            log_id = helper.log_entry(log_data)
            for product, value in iteritems(request.json):
                if str(value) == 'y':
                    products.append(product)

            if len(products) > 0:
                for product in products:
                    task_id = getattr(tasks, product).delay(
                        token,
                        ddi,
                        region,
                        product,
                        str(log_id)
                    )
                    task_ids.append({product: str(task_id)})

            return jsonify(tasks=task_ids), 202
        else:
            return jsonify(
                message='<strong>Error!</strong> Authentication has failed'
                ' due to incorrect token or DDI. Please check'
                ' the token and DDI and try again.'
            ), 401

    @route('/status/<task_id>')
    def get_task_status(self, task_id):
        task = tasks.check_tasks(task_id)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
            }
            if task.info:
                response['result'] = render_template(
                    '_limit_results.html',
                    data=task.info
                )
        else:
            # Something went horribly wrong
            response = {
                'state': task.state,
                'status': str(task.info)  # Error from task
            }

        return jsonify(response)


class GlobalManageView(FlaskView):
    decorators = [check_perms(request)]
    route_base = '/manage'

    @route('/regions', methods=['GET', 'POST'])
    def define_available_regions(self):
        settings = g.db.settings.find_one()
        form = forms.RegionSet()
        if request.method == 'POST' and form.validate_on_submit():
            region = Region(request.form)
            if settings.get('regions'):
                g.db.settings.update(
                    {
                        '_id': settings.get('_id')
                    }, {
                        '$push': {
                            'regions': region.__dict__
                        }
                    }
                )
            else:
                g.db.settings.update(
                    {
                        '_id': settings.get('_id')
                    }, {
                        '$set': {
                            'regions': [region.__dict__]
                        }
                    }
                )
            flash('Region successfully added to system', 'success')
            return redirect(
                url_for('GlobalManageView:define_available_regions')
            )
        else:
            if request.method == 'POST':
                flash(
                    'There was a form validation error, please '
                    'check the required values and try again.',
                    'error'
                )

            return render_template(
                'manage/manage_regions.html',
                form=form,
                regions=settings.get('regions', [])
            )

    @route('/limits', methods=['GET', 'POST'])
    @route('/limits/<limit_id>', methods=['GET', 'POST'])
    def define_limit_maps(self, limit_id=None):
        limit = None
        limits = g.db.limit_maps.find().sort('product')
        if limit_id:
            limit = g.db.limit_maps.find_one({'_id': ObjectId(limit_id)})
            if limit:
                limit = Limit(limit)
                form = forms.LimitMap(obj=limit)
            else:
                flash('Could not find the specified limit', 'error')
                return redirect('/manage/limits')
        else:
            form = forms.LimitMap()

        products = g.db.products.find({'active': True})
        form.product.choices = [
            (product.get('db_name'), product.get('title'))
            for product in products
        ]
        form.product.choices.insert(0, ('', ''))
        if request.method == 'POST' and form.validate_on_submit():
            save_limit = Limit(request.form)
            if limit_id:
                g.db.limit_maps.update(
                    {
                        '_id': ObjectId(limit_id)
                    }, {
                        '$set': save_limit.save_dict()
                    }
                )
                flash('Limit successfully updated', 'success')
            else:
                g.db.limit_maps.insert(
                    save_limit.save_dict()
                )
                flash('Limit successfully added', 'success')

            return redirect('/manage/limits')
        else:
            if request.method == 'POST':
                flash(
                    'There was a form validation error, please '
                    'check the required values and try again.',
                    'error'
                )

        if limit_id and limit:
            return render_template(
                'manage/_edit_limits.html',
                form=form,
                limit=limit
            )
        else:
            return render_template(
                'manage/manage_limits.html',
                form=form,
                limits=limits
            )

    @route('/products')
    def list_products(self):
        products = g.db.products.find()
        return render_template(
            'manage/product_listing.html',
            products=products
        )

    @route('/product/<product>', methods=['GET', 'POST'])
    def manage_products(self, product):
        product_data = self.retrieve_product(product)
        if type(product_data) is str:
            title = "%s Manage Settings" % product.title()
            product_data = None
            form = forms.ManageProduct()
        else:
            title = "%s Manage Settings" % product_data.title
            form = forms.ManageProduct(obj=product_data)

        if request.method == 'POST' and form.validate_on_submit():
            to_save = Product(request.form.to_dict())
            if product_data and product_data.db_name:
                to_save.db_name = product_data.db_name
            else:
                to_save.set_db_name()

            if product_data:
                g.db.products.update(
                    {
                        '_id': ObjectId(product_data.id)
                    }, {
                        '$set': to_save.save_dict()
                    }
                )
                flash('Product was successfully updated', 'success')
            else:
                g.db.products.insert(to_save.save_dict())
                flash('Product was successfully added', 'success')

            return redirect(
                url_for('GlobalManageView:manage_products', product=product)
            )
        else:
            if request.method == 'POST':
                flash('Form was not saved successfully', 'error')

            return render_template(
                'manage/manage_products.html',
                title=title,
                form=form,
                product=product_data,
            )

    @route('/<key>/<action>/<value>')
    def data_type_actions(self, key, action, value):
        change = None
        actions = ['activate', 'deactivate', 'delete']
        maps = {
            'regions': {
                'search': 'regions.abbreviation',
                'redirect': '/manage/regions',
                'db_name': 'settings',
            },
            'limits': {
                'search': '_id',
                'redirect': '/manage/limits',
                'change': 'active',
                'db_name': 'limit_maps',
                'title': 'title'
            }
        }
        if maps.get(key):
            item = maps.get(key)
            if action in actions:
                if item.get('search') == '_id':
                    value = ObjectId(value)

                found = getattr(g.db, item.get('db_name')).find_one(
                    {
                        item.get('search'): value
                    }
                )
                if found:
                    if action == 'delete':
                        keys = item.get('search').split('.')
                        if len(keys) > 1:
                            change = {'$pull': {keys[0]: {keys[1]: value}}}
                    else:
                        if action == 'activate':
                            change = {'$set': {item.get('change'): True}}
                        elif action == 'deactivate':
                            change = {'$set': {item.get('change'): False}}

                    if change:
                        getattr(g.db, item.get('db_name')).update(
                            {
                                item.get('search'): value
                            },
                            change
                        )
                    elif action == 'delete':
                        getattr(g.db, item.get('db_name')).remove(
                            {
                                item.get('search'): value
                            }
                        )

                    if item.get('title'):
                        flash(
                            '%s was %sd successfully' % (
                                found.get(item.get('title')).title(),
                                action
                            ),
                            'success'
                        )
                    else:
                        flash(
                            '%s was %sd successfully' % (
                                value.title(),
                                action
                            ),
                            'success'
                        )
                else:
                    flash(
                        '%s was not found so no action taken' % value.title(),
                        'error'
                    )
            else:
                flash('Invalid action given so no action taken', 'error')
            return redirect(item.get('redirect'))
        else:
            flash('Invalid data key given so no action taken', 'error')
            return redirect('/')

    def retrieve_product(self, product):
        product_slug = helper.slug(product.strip())
        temp_product = g.db.products.find_one({'db_name': product_slug})
        if temp_product:
            return Product(temp_product)

        return str(product)

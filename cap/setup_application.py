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


from flask import Flask, g
from cap.config import config
from datetime import timedelta
from happymongo import HapPyMongo
from flask.ext.cloudadmin import Admin
from flask.ext.cloudauth import CloudAuth
from cap import views, defaults, template_functions


import logging


def create_app(db_name=None):
    app = Flask(__name__)
    app.config.from_object(config)
    if db_name:
        config.MONGO_DATABASE = db_name

    mongo, db = HapPyMongo(config)
    app.permanent_session_lifetime = timedelta(hours=2)

    auth = CloudAuth(app, db)
    app.context_processor(template_functions.view_functions)

    Admin(app)

    @app.before_first_request
    def logger():
        if not app.debug:
            app.logger.addHandler(logging.StreamHandler())
            app.logger.setLevel(logging.INFO)

    @app.before_request
    def before_request():
        g.db, g.auth = db, auth

    defaults.application_initialize(db, app)
    views.BaseView.register(app)
    views.GlobalManageView.register(app)
    views.QueryView.register(app)

    if db_name:
        return app, db
    else:
        return app

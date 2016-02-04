[![Build Status](https://travis-ci.org/oldarmyc/cap.svg?branch=master)](https://travis-ci.org/oldarmyc/cap.svg?branch=master)

#### Cap - Limit Queries

When needing to build out or scale systems for new projects or deployments, it is imperative to ensure that you have the appropriate limits needed to do so. However querying all products and determining those limits can be time consuming and frustrating. Cap makes this easy by querying all of the products at the same time, and showing what you need to know.

You can query all Rackspace API cloud limits for the following products:

- Autoscale
- Big Data
- CBS
- DNS
- Load Balancers
- Servers

These are currently the products where limits can be queried using the API, and you can effectively see where you are at and if you need to raise your existing limits.

After a successful query you will see the following:
- Limit name and the unit of measure if applicable
- Used amount is it can be calculated
- Used percentage or how much you are using of your current limits
- Documentation link describing the limits and how to get them from the API docs
- Direct link to Pitchfork where you can see the call structure, mock the call, or execute the call yourself

The used amount and used percentage are also color coded to help you visually determine how close you are to hitting your limits.
- Green 0% - 60% used
- Yellow - 60.01% - 80% used
- Red - 80.01% - 100% used

To view the public facing application you can visit the following URL: https://cap.cloudapi.co

#### Running the application locally

##### Requirements
- Python 2.7+
- Mongodb
- RabbitMQ

##### Config Files
Within the cap/config directory you will need to make a config.py and celery.py config file that the application will use. Example files are provided and you only need to change the following values.

*Change the following values in config.py for your setup:*  
**MONGO_HOST** : IP/Host of MongoDB server is not using localhost  
**MONGO_PORT** : Database port to use if different than 27017  
**MONGO_DATABASE** : Database name to use and the default is cap  
**ADMIN_USERNAME** = Username of Rackspace cloud account  
**ADMIN_NAME** = Name of user  
**ADMIN_EMAIL** = Email address of user  

*Change the following values in celery.py for your setup:*  
**BROKER_URL** : If not localhost then the location of your rabbitMQ server  
**MONGO_HOST** : IP/Host of MongoDB server is not using localhost  
**MONGO_PORT** : Database port to use if different than 27017  
**MONGO_DATABASE** : Database name to use and the default is cap  

##### Adding products with limits

[CAP Products and Limits](http://a370f2615ebe532b4bde-56882658ef09db12255ddddb1928252a.r62.cf5.rackcdn.com/cap_products_limits.tar.gz)

The download above will provide all of the mongodb bson files for each of the Rackspace products with the mappings for the limits. Once you download the files you can do the following to restore all of the product and limit collections to the cap database. This assumes the database name used is cap, and if it has changed then you will need to alter the command below.

```
tar xzvf cap_products_limits.tar.gz
mongorestore -d cap --drop cap_products_limits/
```

**Note:** If you have added your own products/limits into the collections you can omit the --drop in the call above, and the products and limits will be added to the existing collection.


##### Using Docker Compose

If you have docker and docker compose on your local system I provided the files needed to build the application. You will need a mongo and rabbitMQ system running as well before you run the docker compose commands, and both are required.

Start up rabbitMQ and MongoDB
```
docker run --name rabbit-dev -p "15672:15672" -p "5672:5672" -p "4369:4369" -p "5671:5671" -p "25672:25672" -d rabbitmq:3
docker run --name mongo-dev -p “27017:27017” -d mongo:3.0.2
```

Build and start up the container
```
docker-compose build
docker-compose up
```

**Note:** That when using docker you may need to change the config file values to not point to localhost, depending on how the ports are presented on your machine.

Once everything is up and running you can browse to the IP:PORT to view the application. By default the port is 5000, and can be changed in the docker-compose.yml file.

##### Python virtualenv
**Note:** The below example uses virtualenvwrapper

````
mkvirtualenv cap
cd cap
git clone https://github.com/oldarmyc/cap.git
cd cap
workon cap
````

Install the python requirements in the virtualenv that was created previously
```
pip install -r requirements.txt
```

After you have saved the config files you created above ensure that mongodb and rabbitMQ is up and running. You can run the following command to start the application.
````
python runapp.py
````

Browse to http://localhost:5000 to view the application and login using your Cloud credentials

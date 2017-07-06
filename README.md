[![Build Status](https://travis-ci.org/oldarmyc/cap.svg?branch=master)](https://travis-ci.org/oldarmyc/cap)

#### Cap - Limit Queries

When needing to build out or scale systems for new projects or deployments, it is imperative to ensure that you have the appropriate limits needed to do so. However querying all products and determining those limits can be time consuming and frustrating. Cap makes this easy by querying all of the products at the same time, and showing what you need to know.

You can query all Rackspace API cloud limits for the following products:

- Autoscale
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

#### Running the application locally

##### Requirements
- Python 2.7+
- Mongodb
- RabbitMQ

##### Copy over sample configs
````
cp cap/config/config.example.py cap/config/config.py
cp cap/config/celery.example.py cap/config/celery.py
````

Change the appropriate values in each of the config files. Currently the sample configs are setup for running everything in Docker or localhost but can be changed depending on the environment.

___

#### Build the docker images

##### Start the build
```
docker-compose build
```

##### Bring the containers up and run in the background
```
docker-compose up -d
```

##### Verify that everything is running
```
docker ps
```

You should see four containers running named cap_app, cap_celery, mongo, and rabbitmq. If all four are running then you can browse to `http://localhost:5000` to view the running application.

If you want to view the container logs in-line just omit the -d flag and it will run in the current terminal window. To stop it in this mode just use CTRL-C. If running in detached mode you can use the command `docker logs CONTAINER_ID` to view the specific container log files.

If in detached mode you can use the following command to stop the containers.
```
docker-compose stop
```
___

#### Running it locally?

##### Setup working directory
```
mkdir cap
git clone https://github.com/oldarmyc/cap.git
cd cap
```

#### Setup config files

##### Copy over sample configs
````
cp cap/config/config.example.py cap/config/config.py
cp cap/config/celery.example.py cap/config/celery.py
````

Change the appropriate values in each of the config files. You will need a rabbitmq server and a mongo server to run locally. These can both be run in docker without issues to avoid having to install both services, but will need to be accessible from localhost.

RabbitMQ docker example run command
```
docker run --name rabbit-dev -p "15672:15672" -p "5672:5672" -p "4369:4369" -p "5671:5671" -p "25672:25672" -d rabbitmq
```

MongoDB docker example run command
```
docker run --name mongo-dev -p "27017:27017" -d mongo
```

##### Install packages
Install base packages needed for the application
```
pip install -r requirements.txt
```

##### Starting the application
```
python runapp.py
```

___

#### Running Tests

##### Ensure you have the testing requirements installed
```
pip install -r dev-requirements.txt
```

##### Running tests with coverage report
```
nosetests --with-coverage --cover-erase --cover-package cap
```

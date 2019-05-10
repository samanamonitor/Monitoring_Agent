# Monitoring Agent  
## Installation
The following installation is within the context of installing the project on an Ubuntu 14.04 system.
### Setup MongoDB
* Follow the instructions to install mongoDB [here](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).
* After installing it, enter a mongo shell script by running `mongo` and create a database called `monitoringAgentDB` with a collection called `defaultConfig` with one document that has the default values for an Agent's configuration that is desired.
```shell
$ mongo
> use monitoringAgentDB
> db.defaultConfig.insert(<defaultdoc>)
```
### Setup Elasticsearch (for searches by `domain` and `hostname`)
This is an optional feature. If you would like the feature, follow the installation instructions for installing Elasticsearch [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/targz.html).
### Generate Google OAuth 2.0 client credentials
Follow instructions [here](https://developers.google.com/adwords/api/docs/guides/authentication#webapp) to generate a Google OAuth client ID and secret.
### Install Apache and Git
```shell
$ sudo apt install apache2 apache2-dev git
```
### Install Python 3
```shell
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt update
$ sudo apt install python3.6 python3.6-dev
```
### Setup mod_wsgi Apache module
#### Install mod_wsgi
* Download a copy of the file to the home folder. The url for the source should be found here [here](https://github.com/GrahamDumpleton/mod_wsgi/releases). Doing this should look somethin like:
```shell
$ wget https://github.com/GrahamDumpleton/mod_wsgi/archive/<version-number>.tar.gz
```
* Unpack the downloaded file using `tar`. Doing this should look something like:
```script
$ tar xvfz <filename>
```
* Change directory into the unpacked file and configure the installation with the path of the Python 3 that was installed here. Sould look something like this:
```script
$ cd <module-version>
$ ./configure  --with-python=/usr/bin/python3.6
```
* Make the installation and install it.
```script
$ make
$ make install
```
If there were any problems in installing mod_wsgi, refer to the installation guide [here](https://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html).
#### Configure Apache to use mod_wsgi
* Clone this repository to the home folder
```shell
$ git clone https://github.com/samanamonitor/Monitoring_Agent.git
```
* Include mod_wsgi to Apache, and add the mod_wsgi configuration file. 
```script
$ sudo cp ~/Monitoring_Agent/mod_wsgi.load /etc/apache2/mods-available/mod_wsgi.load
$ sudo ln -s /etc/apache2/mods-available/mod_wsgi.load /etc/apache2/mods-enabled/mod_wsgi.load
$ sudo cp ~/Monitoring_Agent/mod_wsgi.conf /etc/apache2/mods-available/mod_wsgi.conf
$ sudo ln -s /etc/apache2/mods-available/mod_wsgi.conf /etc/apache2/mods-enabled/mod_wsgi.conf
```
### Setup Monitoring Agent Project
* Create a `.flaskenv` file in the project root directory of the form `.flaskenv.example` (found in the project root directory). The variables found in `.flaskenv.example` are described as follows:
 
  * `FLASK_APP`: Used for testing for runing the flask app locally. Set it to `test.py` so that runing `flask run` will host the app on localhost:5000
  * `SECRET_KEY`: Used for CSRF tockens. Reccomended for production.
  * `FLASK_ENV`: Used for debugging. Set this to `development` to run the app on debug mode. (WARNING: Do not set in production)
  * `HASH_SALT`: (required) A hash salt for the keys made for agent data documents
  * `PAGINATION_SIZE`: (optional) Set to a non-negative integer that sets how many entries can be listed in the index page at a time. Default value is `50`.
  * `GOOGLE_CLIENT_ID`: web client ID for Google OAuth 2.0 credentials
  * `GOOGLE_CLIENT_SECRET`: web client secret for Google OAuth 2.0 credentials
  * `MONGO_URI`: (optional) When not set, it's default value is `mongodb://localhost:27017/monitoringAgentDB`
  * `ELASTICSEARCH_URL`: (optional) If not set, search functionality is disabled. If elasticsearch is installed locally with defaults, this should be set to `http://localhost:9200`. A JSON file should appear at that URL if Elasticsearch is running. If not, try starting it by running `$ sudo service elasticsearch start`.
* Copy the project to Apache's `www` directory. Should look something like this:
```script
$ sudo cp -r ~/Monitoring_Agent /var/www/Monitoring_Agent
```
* Look over `monitoring_agent.conf` if it has information that does not agree with your system (e.g. user, group, etc.)
* Add `monitoring_agent.conf` to Apache's configurations. Should look something like this:
```script
sudo cp ~/Monitoring_Agent/monitoring_agent.conf /etc/apache2/conf-available/monitoring_agent.conf
sudo ln -s /etc/apache2/conf-available/monitoring_agent.conf /etc/apache2/conf-enabled/monitoring_agent.conf
```
* Reload Apache
```script
$ sudo service apache2 reload
```

# Linux Server Configuration with LightSail

## Set up an amazon lightsail instance

Select OS only and ubuntu 16.04 LTS
![001](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/001_lightsail_create.jpg)

Name your server
![002](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/002_lightsail_create.jpg)

## Configure Putty for access through Windows
Click the newly created instance and then the accounts page:
https://lightsail.aws.amazon.com/ls/webapp/account/keys
Download the newly created key (the .pem file) and save it to your computer.
You will need this file to generate the key pairs to access your amazon instance.
Open the putty key generator and browse to the .pem file in the File menu.

![003](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/003_putty.jpg)


We want to save the private key. So select save private key and save it to your computer. The saved file will be a .ppk

![004](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/004_putty.jpg)

This is the private key for the Ubuntu user which lets us SSH for the first time into our instance.
Configure putty to connect to our server:
Open putty and set the host name/ IP address for our server:
3.121.94.16

![005](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/005_putty.jpg)

Set the putty connection to use the private key we setup above:
Go to SSH and Auth and browse to the above saved .ppk file.

![006](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/006_putty.jpg)

## Connecting for the first time

We can now connect, click open.
When prompted for a user name enter: ubuntu

![007](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/007_ubuntu.jpg)

Update the server:
> sudo apt-get update
> sudo apt-get upgrade

## Create the grader user

Setting up the grader user
Create the grader user:
> sudo adduser grader
Give the grader user sudo access:
sudo visudo

![008](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/008_ubunut.jpg)

## Make the grader sudo

Under the line that gives the root user sudo access, add the following:
grader ALL=(ALL:ALL) ALL
Configuring SSH to non-default port

## Set up lightsail firewall

Click the networking tab and add a new custom rule for the TCP protocol on 2200.

![009](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/009_firewall.jpg)

## Create SSH keys for the grader

Create the ssh keys for grader
Creating the keys can be done in the putty key generator:
Click generate:



## Install the grader's public key on the server

When putty has finished generating the keys save them to a secure location on your hard disk on your local machine (both the private and public key).
Now on the linux instance go to the grader’s home directory

>cd /home/grader

>sudo mkdir .ssh

>cd .ssh

>sudo nano authorized_keys

Paste this key into the file and save.

## Configure putty to use this key:
Just like we did with the default Ubuntu user above we set putty to use our private key:

![010](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/010_putty_keys.jpg)


**Test your connection, click open and you should connect as the grader.**


## Securing Firewall and ports

We can now alter our server to only allow SSH on 2200
>sudo nano /etc/ssh/sshd_config
Change the port entry from 22 to 2200:
Port 2200
Change PermitRootLogin prohibit-password to:
PermitRootLogin no
Make sure password authentication is switched off so we can only use keys:
PasswordAuthentication No

>sudo service ssh restart
**Make sure the service restarts, if there is an error make note and fix the file else you can lock yourself out of the server**

Setting up the fire inside the local instance:
> sudo ufw default deny incoming
> sudo ufw default allow outgoing

> sudo ufw allow 2200
> sudo ufw allow 2200/tcp

> sudo ufw allow 80
> sudo ufw allow 80/tcp

> sudo ufw allow 123
> sudo ufw allow 123/udp

Enable the firewall
> sudo ufw enable 
Check the status:
>sudo ufw status

![011](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/011_ubuntu_ufw.jpg)

## Install apache

Install apache
> sudo apt-get install apache2

Check the installation is correct by entering on your local computer the IP address of your server into the address bar of your browser you should get the default apache web page:

![012](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/012_apache_default.jpg)

Installing the components to run WSGI python apps:
now install the apache python components:

> sudo apt-get install libapache2-mod-wsgi python-dev

Make sure that WSGI is enabled with (it probably is by default):

> sudo a2enmod wsgi

## Installing dependencies

Install GIT:

> sudo apt-get install git


Install PostGres SQL:

> sudo apt-get install postgresql


## Set up the default database:

change to the postgres user:

> sudo su - postgres

Launch psql:

> psql

At the psql prompt we can now create the database and user
postgres=# CREATE USER catalog_user WITH PASSWORD 'udacitycatalogapp';
postgres=# ALTER USER catalog_user CREATEDB;
postgres=# CREATE DATABASE catalog WITH OWNER catalog_user;

Set the correct privileges:
postgres=# REVOKE ALL ON SCHEMA public FROM public;
postgres=# GRANT ALL ON SCHEMA public TO catalog_user;

Quit postgres
postgres=# \q
> exit 
We return to the user we logged in as (grader or Ubuntu).

## Python dependencies:

Install pip

> sudo apt-get install python-pip

- Install Flask
> pip install flask

- Install SqlAlchemy
> pip install sqlalchemy

- Install Oauth client
> pip install oauth2client
- Install httplib2
> pip install httplib2
- Install requests
>pip install requests
- Install psycopg2
>pip install psycopg2


We can now setup our flask application
>cd /var/www
> sudo mkdir catalog
We will place the flask app in the catalog folder.
>cd catalog
Download the repository:
sudo git clone https://github.com/AndFran/udacity_fullstack_nano.git
Rename any directories etc.
The catalog application is now in the folder:
/var/www/catalog/catalog/


![013](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/013_apache_catalog_folder.jpg)


## Create the conf file for apache

>sudo nano /etc/apache2/sites-available/catalog.conf
<VirtualHost *:80>

        ServerName http://ec2-3-121-94-16.eu-central-1.compute.amazonaws.com/
        
        ServerAdmin me
        
        WSGIScriptAlias / /var/www/catalog/catalog.wsgi
        
        <Directory /var/www/catalog/catalog/>
        
            Order allow,deny
            
            Allow from all
            
        </Directory>
        
        Alias /static /var/www/catalog/catalog/static
        
        <Directory /var/www/catalog/catalog/static/>
        
            Order allow,deny
            
            Allow from all
            
        </Directory>
        
        ErrorLog ${APACHE_LOG_DIR}/error.log
        
        LogLevel warn
        
        CustomLog ${APACHE_LOG_DIR}/access.log combined
        
</VirtualHost>

Notice the paths carefully.
Enable the virtual host:
>sudo a2ensite catalog
Activate the new configuration:
>sudo service apache2 reload

## Create the WSGI file

We now create the .wsgi file
>cd /var/www/catalog
>sudo nano catalog.wsgi

import sys
sys.path.insert(0, “/var/www/catalog”)
from catalog import app as application
application.secret_key='f1ef9d3b-b3db-4c30-ab6d-cc99095a4fb5'

## Changes in the python files from the base project

Changes in the python files:
The following changes were made in models.py
The file on the repository init.py was renamed to __init__.py to make the catalog folder a python package.
The follow changes were made inside

Disable the default apache site and enable the catalog app:
>sudo a2dissite 000-default.conf
>sudo a2ensite catalog.conf
>sudo service apache2 reload


Reset the apache service:
>sudo service apache2 restart

## Get a domain name for the server

The server as it stands just has an IP address:
3.121.94.16

Inside the light sail web interface click and get a static IP address under the networking tab.
Now with this static IP use a DNS lookup to get a server name it will be something like:

http://ec2-3-121-94-16.eu-central-1.compute.amazonaws.com/




## Check the catalog app loads as the default application:

Go to the http://ec2-3-121-94-16.eu-central-1.compute.amazonaws.com/

![014](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/014_app_running.jpg)

## Fixing domain names for google OAuth.

Google Oauth does not use IP addresses. So remember to add the domain:

http://ec2-3-121-94-16.eu-central-1.compute.amazonaws.com/

To the google authorized server list for OAuth to still work.


## Sources
http://www.islandtechph.com/2017/10/23/how-to-deploy-a-flask-python-3-5-application-on-a-live-ubuntu-16-04-linux-server-running-apache2/
https://hk.saowen.com/a/0a0048ca7141440d0553425e8df46b16cdf4c13f50df4c5888256393d34bb1b9
https://www.digitalocean.com/community/questions/how-do-i-remove-apache2-ubuntu-default-page
https://blog.codeasite.com/how-do-i-find-apache-http-server-log-files/
http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
























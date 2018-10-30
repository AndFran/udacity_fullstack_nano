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

Setting up the grader user
Create the grader user:
> sudo adduser grader
Give the grader user sudo access:
sudo visudo

![008](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/008_ubunut.jpg)

Under the line that gives the root user sudo access, add the following:
grader ALL=(ALL:ALL) ALL
Configuring SSH to non-default port
Click the networking tab and add a new custom rule for the TCP protocol on 2200.

![009](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/009_firewall.jpg)

Create the ssh keys for grader
Creating the keys can be done in the putty key generator:
Click generate:

![010](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/010_putty_keys.jpg)

When putty has finished generating the keys save them to a secure location on your hard disk on your local machine (both the private and public key).
Now on the linux instance go to the grader’s home directory
>cd /home/grader
>sudo mkdir .ssh
>cd .ssh
>sudo nano authorized_keys
Paste this key into the file and save.
Configure putty to use this key:
Just like we did with the default Ubuntu user above we set putty to use our private key:

![011](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/011_ubuntu_ufw.jpg)


Test your connection, click open and you should connect as the grader.

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


![012](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/012_apache_default.jpg)



![013](https://github.com/AndFran/udacity_fullstack_nano/blob/master/server_configuration/images/013_apache_catalog_folder.jpg)







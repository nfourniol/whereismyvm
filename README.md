# WhereIsMyVM

## How to configure the hypervisors for exploration (ESXi, Proxmox, ...)
In the project's root directory, create a file named 'hypervisor.yaml' using 'hypervisor.yaml.sample' as a template.

This software supports hot reload, so any changes made to hypervisor.yaml are immediately reflected without the need for restarting the application.

This file use the following structure :

```
esxi:
  -
    host: proxmox1.whereismyvm.com:8006
    type: proxmox
    login: proxmoxlogin1
    passwd: mdp1
  -
    host: proxmox2.whereismyvm.com
    type: proxmox
    login: proxmoxlogin2
    passwd: mdp2
  -
    host: esxi1.whereismyvm.com
    type: esxi
    login: esxilogin1
    passwd: mdp1
  - 
    host: esxi2.whereismyvm.com
    type: esxi
    login: esxilogin2
    passwd: mdp2
  - 
    host: proxmox1.whereismyvm.com
    type: proxmox # be careful, it's juste here as an example, but proxmox implementation doesn't exist for the moment
    login: proxmoxlogin3
    passwd: mdp3
```

**Security** :
- ESXi users must have read only access
- Proxmox users must have read only access
- ```chmod 660 hypervisor.yaml```
- if you fork this project be sure your .gitignore file contains *.env, config.yaml, hypervisor.yml (we don't want our password to be shared)

## How to manage other hypervisors than ESXi and Proxmox

***Currently compatible with VMWare and Proxmox, but you can easily implement solutions for other kind of hypervisors***, just by using esxi.py or proxmox.py as a template.

And then modify the factory method getHypervisorService to return the new implemented hypervisor service.


## config.yaml
In the root folder, a 'config.yaml' file should be created by using the 'config.yaml.sample' file as a template.

## Development environment
You should define the following environment variables :

DJANGO_DEBUG

DJANGO_SECRET_KEY

DJANGO_DEBUG will take the value True

DJANGO_SECRET_KEY will take a random value which contains special characters and at least 15 characters.

These variables are read in settings.py file.

You can use Visual Studio Code as an IDE. And you should install the python and django plugins.

## Docker container for quick test
First clone this repository.

Then go into the <ROOT_DIRECTORY>/.docker directory.

Create config.yaml by copying <ROOT_DIRECTORY>/config.yaml.sample

Create hypervisor.yaml by copying <ROOT_DIRECTORY>/hypervisor.yaml.sample

Edit these two files, and fill the values required.

In a windows command prompt:
```
cd <ROOT_DIRECTORY>/.docker
docker build --no-cache -t whereismyvm:v1.0 .
docker run --name whereismyvm -v %cd%\config.yaml:/var/www/webtool/whereismyvm/config.yaml -v %cd%\hypervisor.yaml:/var/www/webtool/whereismyvm/hypervisor.yaml -d -p 7777:7777 whereismyvm:v1.0
```
In a windows powershell prompt:
```
cd <ROOT_DIRECTORY>/.docker
docker build --no-cache -t whereismyvm:v1.0 .
docker run --name whereismyvm -v $(pwd)\config.yaml:/var/www/webtool/whereismyvm/config.yaml -v $(pwd)\hypervisor.yaml:/var/www/webtool/whereismyvm/hypervisor.yaml -d -p 7777:7777 whereismyvm:v1.0
```

In a linux prompt:
```
cd <ROOT_DIRECTORY>/.docker
docker build --no-cache -t whereismyvm:v1.0 .
docker run --name whereismyvm -v $(pwd)/config.yaml:/var/www/webtool/whereismyvm/config.yaml -v $(pwd)/hypervisor.yaml:/var/www/webtool/whereismyvm/hypervisor.yaml -d -p 7777:7777 whereismyvm:v1.0
```

Then you can see your container logs with:
```
docker logs -f whereismyvm
```

Your can access the web at the following URL: http://localhost:7777/

NOTE: hypervisor.yaml must have been created with the values from your esxi servers otherwise you'll get an error when accessing the url.

## Production environment

### Environment Variables
You should define the following environment variables :
DJANGO_DEBUG
DJANGO_SECRET_KEY

DJANGO_DEBUG will take the value False
DJANGO_SECRET_KEY will take a random value which contains special characters and at least 15 characters.

### Install linux requirements
```
dnf -y install git httpd
```

Install python 3 and pip3 if not present on your server: you can follow this link that allow you to install a specific python3 version https://nicodevlog.com/2022/05/17/python-and-virtual-environments-on-linux-os/


### Deployment
We will use the python gunicorn server, and as a frontal webserver we'll use apache (as well as you can use nginx).
Here we are on linux but you can deploy also on windows.

### Deploy the sources
Create a linux user called for instance webtool, with a home directory called /home/webtool

Install python3 if not present on your linux server.

Now log on as this webtool user and deploy the sources from github:
```
sudo su - webtool
git clone https://github.com/nfourniol/whereismyvm.git
cd whereismyvm
python3 -m venv venv
source ./venv/bin/activate
pip3 install -f requirements.txt
```

### Start gunicorn server
```
sudo su - webtool
cd whereismyvm
source venv/bin/activate
gunicorn whereismyvm.wsgi --bind 127.0.0.1:8888 --daemon
```

#### Apache configuration
Add the following host information (you can replace 80 port by 443 port in case of https)
```
<VirtualHost *:80>
    ServerName whereismyvm.yourdomain.com
    ServerAlias whereismyvm.yourdomain.com
    ServerAdmin youremail@whereismyvm.yourdomain.com

    DocumentRoot /home/webtool/whereismyvm

    ProxyPass / http://127.0.0.1:8888/
    ProxyPassReverse / http://127.0.0.1:8888/
</VirtualHost>
```
```
systemctl reload httpd
```
Then you can access your whereismyvm app on the url http://whereismyvm.yourdomain.com/

## How to restart server in case of an error
As the webtool user :
```
ps -C gunicorn fc -o ppid,pid,cmd
```
You'll get this kind of output:
```
[webtool@yourserver whereismyvm]$ ps -C gunicorn fc -o ppid,pid,cmd
 PPID   PID CMD
        1 12463 gunicorn
12463 12464  \_ gunicorn
```
The first line correspond to the gunicorn master process, the second one is for the worker process.

Execute the following command:
```
kill -HUP 12463
```
Wait some seconds before testing again the app url: it should work again.

If the app didn't come back after 30 seconds, you can execute the following command:
```
kill 12463
```

## Update application source code and empty the server cache ##
You can deploy use whatever mean for deploying (ftp, git pull, ...)

First empty the apache cache:
```
service httpd reload
```
Then restart the gunicorn server:
```
ps -C gunicorn fc -o ppid,pid,cmd
```
see explanation in previous paragraph, to identify the PID to kill:
```
kill -HUP 12463
```

## Generation of a pdf listing the VMs ##
Access to the url <whereismyvm_base_url>/pdf/
The ac
Access to this URL triggers the generation and sending of a pdf to the emails specified in mail_recipients in the config.yaml file.

If you want this to be triggered by a linux cron, all you need to do is create a cron job that makes a call to this url (using curl, for example).
Currently, the cron job is run by the user in which the application is deployed:
```
00 10 * * 6 curl --url <whereismyvm_base_url>/pdf/ --output ~/cron_curl_allvm_pdf.log >> ~/cron_curl_allvm_pdf.log 2>&1
```

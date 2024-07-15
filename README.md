# WhereIsMyVM

## How to configure the hypervisors for exploration (ESXi, Proxmox, ...)
In the project's root directory, create a file named 'hypervisor.yaml' using 'hypervisor.yaml.sample' as a template.

Currently compatible with VMWare only, but you can easily implement solution for proxmox, virtuozzo, or other, just by using esxi.py as a template.

And then modify the factory method getHypervisorService to return the new implemented hypervisor service.

This software supports hot reload, so any changes made to hypervisor.yaml are immediately reflected without the need for restarting the application.

This file use the following structure :

```
esxi:
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
    type: proxmox
    login: proxmoxlogin3
    passwd: mdp3
```

**Security** :
- ESXi users must have only read access
- ```chmod 660 hypervisor.yaml```
- if you fork this project be sure your .gitignore file contains *.env, *.yaml, *.yml (we don't want our password to be shared)

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

## Production environment

### Environment Variables
You should define the following environment variables :
DJANGO_DEBUG
DJANGO_SECRET_KEY

DJANGO_DEBUG will take the value False
DJANGO_SECRET_KEY will take a random value which contains special characters and at least 15 characters.

### Install linux requirements
```
dnf -y install git python3 httpd python3-pip
```

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

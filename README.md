# TransIP DDNS service
Update DNS A records for those with dynamic ip-addresses.

## Why:
Not everyone has a static ip-address at home but still wants to access their services or website using a domain.
This will update the A records for your domains hosted on TransIP.

## How:
This service will grab its current public ip-address and compare it to the A records using the TransIP API.
These A records are defined in the script in fqdn format.

## Prerequisite:
- An account on TransIP
- A domain name registered on TransIP
- Python 3.7+ with pip
- TransIP API private key (generated in your TransIP Controlpanel)

## Installation:
```
pip install -r requirements.txt
```

## Config:

### All scenarios
Log in to your account and go to "my account" & API.
First off enable the API by setting the toggle just under API-settings to on.
Create a new keypair (without ip whitelist) and save the key for now.

Copy `src/lib/transip_settings.py.example` to `src/lib/transip_settings.py` and fill in your TransIP username and the key you generated:
```python
# TransIP API Settings
LOGIN = 'USERNAME'

PRIVATE_KEY = '''-----BEGIN PRIVATE KEY-----
YOURKEYHERE
-----END PRIVATE KEY-----'''
```

Alternatively, set the following environment variables instead of using the settings file:
```
TRANSIP_LOGIN=yourusername
TRANSIP_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOURKEYHERE\n-----END PRIVATE KEY-----
# or point to a key file:
TRANSIP_PRIVATE_KEY_FILE=/path/to/private_key.pem
```

### Local webserver without static ip

Edit `src/checkwan.py` and change the domains (you can add and delete them) and define a logfile.
Make sure to note down the domains in fqdn format.
```python
# SETTINGS
# The domains to edit
domains = [
    '@.domain.tld',
    '*.domain.tld',
    'sub.domain.tld',
    'sub.sub.domain.tld',
]

# Logfile to log output to
logfile = '/var/log/ddns.log'
```

Test if everything works as expected:
```
michael@ws-michael:~$ python3 src/checkwan.py
Updating old ip 1.2.3.4, with: 12.34.56.78 for: @.domain.tld
DNS updated successfully!
No update required, current IP: 12.34.56.78 is unchanged for: *.domain.tld
No update required, current IP: 12.34.56.78 is unchanged for: sub.domain.tld
No update required, current IP: 12.34.56.78 is unchanged for: sub.sub.domain.tld
```

Finally, create a cronjob to make sure the A records are being kept up to date even when you're not watching:
```
0 * * * * root python3 /path/to/transip-ddns/src/checkwan.py
```

### Remote webserver with static ip

Edit `src/remoteddns.py` and change the log path to your liking and generate a random key.
The key will be used by the client to authenticate.
```python
# Logfile to log output to
logfile = '/var/log/ddns.log'

# The authentication key (override via REMOTEKEY environment variable)
KEY = os.environ.get('REMOTEKEY', 'Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY')  # Generate your own random key here
```

Run the Flask application on your webserver:
```
cd src && python3 remoteddns.py
# or with gunicorn for production:
cd src && gunicorn -w 4 -b 0.0.0.0:80 remoteddns:app
```

Test if everything works as expected.
Use curl or browse to your webserver's address and include the key and domain in your request.
```
michael@ws-michael:~$ curl "http://remotewebserver.tld/?domain=@.domain.tld&key=Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY"
Updating old ip 1.2.3.4, with: 12.34.56.78 for: @.domain.tld
DNS updated successfully!
```

Finally, create a cronjob to make sure the A records are being kept up to date even when you're not watching:
```
0 * * * * root curl "http://remotewebserver.tld/?domain=@.domain.tld&key=Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY"
```

This application works behind a reverse-proxy like haproxy/nginx.
To make this happen just forward the X-Forwarded-For header to this application with the client ip.
Example for nginx:
```
server {
        listen 80;

        server_name remotewebserver.tld;

        location / {
         proxy_pass          http://ddns-application-server;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_redirect off;
        }
}
```


## Running in Docker

### images
This repo contains two images, both hosted at hub.docker.com as public images:
```
mbchristoff/transip-ddns:apache-latest
mbchristoff/transip-ddns:cli-latest
```
The apache image will contain everything needed to run the remote DDNS script in a container with a built-in web server (Gunicorn).
The cli container will simply run the checkwan Python script and exit afterwards.

### usage

#### config
Copy `src/lib/transip_settings.py.example` to `transip_settings.py`, fill in your credentials, and mount it to your container:
```
-v "/path/to/transip_settings.py:/var/www/html/lib/transip_settings.py"
```

Alternatively, pass credentials via environment variables:
```
-e TRANSIP_LOGIN=yourusername
-e TRANSIP_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOURKEY\n-----END PRIVATE KEY-----"
```

The domains will be passed through as an environment variable:
```
-e DOMAINS="@.domain.tld,*.domain.tld,sub.domain.tld"
```

The remote key for the web endpoint can be added as an environment variable:
```
-e REMOTEKEY=mysupersecurekey
```

Log files will be written to `/var/log/ddns.log`. It is possible to mount this folder to a folder on your host system to make them persistent.

#### Full example commands:
```
docker run -p 8080:80 -e DOMAINS="@.domain.tld,*.domain.tld,sub.domain.tld" -e REMOTEKEY=mysupersecurekey -v "/path/to/transip_settings.py:/var/www/html/lib/transip_settings.py" -v "/path/to/logs/:/var/log/" mbchristoff/transip-ddns:apache-latest

docker run -e DOMAINS="@.domain.tld,*.domain.tld,sub.domain.tld" -v "/path/to/transip_settings.py:/var/www/html/lib/transip_settings.py" -v "/path/to/logs/:/var/log/" mbchristoff/transip-ddns:cli-latest
```

#### Docker-compose
Example docker-compose.yaml files are included in this repo. Simply edit and copy these files to a server running docker & docker-compose and run `docker-compose up`.


## Bonus

Not defining a domain will return your current public ip-address:
```
curl "http://remotewebserver.tld/"
12.34.56.78
```

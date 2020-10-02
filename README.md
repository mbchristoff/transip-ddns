# TransIP DDNS service
Update DNS A records for those with dynamic ip-addresses.

## Why:
Not everyone has a static ip-address at home but still wants to access their services or website using a domain.
This will update the A records for your domains hosted on TransIP.

## How:
This service will grab it's current public ip-address and compare it to the A records using the TransIP API.
These A records are defined in the script in fqdn format.

Both having a local 

## Prerequisite:
- An account on TransIP
- A domain name registered on TransIP
- A (web)server with (php7.x) with php7.x-soap
- A client (or the server itself) that can execute cronjobs
- TransIP API libraries (included in the repo)

## Config:

### All scenarios
Log in to your account and go to "my account" & API.
First off enable the API by setting the toggle just under API-settings to on.
Create a new keypair (without ip whitelist) and save the key for now.

Edit "src/lib/Transip/ApiSettings.php" and fill in your TransIP username and the key you generated.
```
......................................................
    /**
     * Your login name on the TransIP website.
     *
     */
    public static $login = 'USERNAME';

    /**
     * One of your private keys; these can be requested via your Controlpanel
     */
    public static $privateKey = '-----BEGIN PRIVATE KEY-----
YOURKEYHERE
-----END PRIVATE KEY-----';
}
....................................................
```

### Local webserver without static ip

Edit "src/checkwan.php" and change the domains (you can add and delete them) and define a logfile.
Make sure to note down the domains in fqdn format.
```
......................................................
// SETTINGS
// The domain to edit
$domains []= '@.domain.tld';
$domains []= '*.domain.tld';
$domains []= 'sub.domain.tld';
$domains []= 'sub.sub.domain.tld';

// Logfile to log output to
$logfile = '/var/log/nginx/ddns.log';

....................................................
```

Copy the src folder to your webserver and test if everything works as expected.
```
michael@ws-michael:~$ php7.4 /var/www/local/html/transip-ddns/checkwan.php 
Updating old ip 1.2.3.4, with: 12.34.56.78 for: @.domain.tld
DNS updated successfully!
No update required, current IP: 12.34.56.78 is unchanged for: *.domain.tld
No update required, current IP: 12.34.56.78 is unchanged for: sub.domain.tld
No update required, current IP: 12.34.56.78 is unchanged for: sub.sub.domain.tld
```

Finally, create a cronjob to make sure the A records are being kept up to date even when you're not watching:
```
0 * * * * root "php7.x /path/to/script/transip-ddns/checkwan.php"
```

### Remote webserver with static ip


Edit "remoteddns.php" and change the log path to your liking and generate a random key.
The key will be used by the client to authenticate.
```
......................................................
// Variables

// Logfile to log output to
$logfile = '/var/log/nginx/ddns/remote.log'; //Make sure the path is writable

// The authentication key
define('KEY', 'Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY'); //Generate your own random key here
......................................................
```

Copy the src folder to your webserver and test if everything works as expected.
Use curl or browse to your webserver's address and include the key and domain in your request.
```
michael@ws-michael:~$ curl "http://remotewebserver.tld/transip-ddns/remoteddns.php?domain=@.domain.tld&key=Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY"
Updating old ip 1.2.3.4, with: 12.34.56.78 for: @.domain.tld
DNS updated successfully!
```

Finally, create a cronjob to make sure the A records are being kept up to date even when you're not watching:
```
0 * * * * root " curl "http://remotewebserver.tld/transip-ddns/remoteddns.php?domain=@.domain.tld&key=Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY"
```

## Running in Docker

### images
This repo contains two images, both hosted at hub.docker.com as public images:
```
mbchristoff/transip-ddns:apache-latest
mbchristoff/transip-ddns:cli-latest
```
The apache image will contain everything needed to run the scripts in a container with built in webserver.
The cli container will simply run the php script and exit afterwards.

### usage

#### config
Edit "src/lib/Transip/ApiSettings.php" as described in "All scenarios" above and mount it to your container as such:
```
-v "/path/to/ApiSettings.php=/var/www/html/lib/Transip/ApiSettings.php
```

The domains will be passed through as environment variables as such:
```
-e DOMAINS="@.domain.tld,*.domain.tld,sub.domain.tld"
```
These domains will be parsed and placed in the checkwan.php script.

The remote key can be added for remoteddns.php can be added as environment variable as well:
```
-e REMOTEKEY=mysupersecurekey
```

Log files will be written to /var/log/ddns.log, it's possible to mount this folder to a folder on your host system to make them persistent.

#### Full example commands:
```
docker run -p 8080:80 -e DOMAINS="@.domain.tld,*.domain.tld,sub.domain.tld" -v "/path/to/ApiSettings.php=/var/www/html/lib/Transip/ApiSettings.php" -v "/path/to/logs/=/var/log/" mbchristoff/transip-ddns:apache-latest

docker run -e DOMAINS="@.domain.tld,*.domain.tld,sub.domain.tld" -e REMOTEKEY=mysupersecurekey -v "/path/to/ApiSettings.php=/var/www/html/lib/Transip/ApiSettings.php" -v "/path/to/logs/=/var/log/" mbchristoff/transip-ddns:cli-latest
```

#### Docker-compose
Example docker-compose.yaml files are included in this repo, simply edit and copy these files to a server running docker & docker-compose and run docker-compose up.


## Bonus

Not definining a domain will return your current public ip-address
```
curl "http://remotewebserver.tld/transip-ddns/remoteddns.php"
12.34.56.78
```

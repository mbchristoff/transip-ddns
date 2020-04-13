# TransIP DDNS service
Update DNS A records for those with dynamic ip-addresses.

## Why:
Not everyone has a static ip-address at home but still wants to access their services or website using a domain.
This will update the A records for your domains hosted on TransIP.

## How:
This service will grab it's current public ip-address and compare it to the A records using the TransIP API.
These A records are defined in the script in fqdn format.

## Prerequisite:
- An account on TransIP
- A domain name registered on TransIP
- A webserver with (php7.x) with php7.x-soap
- A client (or the webserver itself) that can execute cronjobs
- TransIP API libraries (included in the repo)

## Config:

Log in to your account and go to "my account" & API.
First off enable the API by setting the toggle just under API-settings to on.
Create a new keypair (without ip whitelist) and save the key for now.

Edit "lib/Transip/ApiSettings.php" and fill in your TransIP username and the key you generated.
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

Edit "chechwan.php" and change the domains (you can add and delete them) and define a logfile.
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

Copy this folder to your webserver and test if everything works as expected.
Use curl or browse to your webserver's internal ip (or 127.0.0.1 on the webserver itself).
```
michael@ws-michael:~$ curl http://192.168.1.2/transip-ddns/checkwan.php
Updating old ip 1.1.1.1, with: 12.34.56.78for: @.domain.tld
No update required, current IP: 12.34.56.78 is unchanged for: *.domain.tld
No update required, current IP: 12.34.56.78 is unchanged for: sub.domain.tld
No update required, current IP: 12.34.56.78 is unchanged for: sub.sub.domain.tld
```

Finally, create a cronjob to make sure the A records are being kept up to date even when you're not watching:
```
0 * * * * root curl http://192.168.1.1/transip-ddns/checkwan.php
```
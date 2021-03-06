#!/bin/bash

# Set remote key for remoteddns.php
if [[ $REMOTEKEY ]]; then
    sed -i "s/Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY/${REMOTEKEY}/g"  /var/www/html/remoteddns.php
fi

# Remove example domains
sed -i '/$domains \[\]=/d' /var/www/html/checkwan.php

# Create an array from domains
ARRAY="${DOMAINS//,/" "}"

# Add set domains to checkwan.php
for DOMAIN in $ARRAY;
do
    sed -i "/The domain to edit/ a \$domains \[\]= \"${DOMAIN}\";" /var/www/html/checkwan.php
done

# Start apache
tail -f /var/log/ddns.log & \
apache2-foreground

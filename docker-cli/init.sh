#!/bin/sh

# Remove example domains
sed -i '/$domains \[\]=/d' /var/www/html/checkwan.php

# Create an array from domains
ARRAY="${DOMAINS//,/" "}"

# Add set domains to checkwan.php
for DOMAIN in $ARRAY;
do
    sed -i "/The domain to edit/ a \$domains \[\]= \"${DOMAIN}\";" /var/www/html/checkwan.php
done

# Start checkwan
php /var/www/html/checkwan.php
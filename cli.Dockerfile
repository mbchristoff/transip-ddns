FROM php:cli-alpine
LABEL maintainer="MBchristoff"

ENV LOG_STDOUT="" \
    LOG_STDERR="" \
    LANG="C.UTF-8" \
    LC_ALL="C.UTF-8"

# Install extra dependencies
RUN apk add --no-cache \
        libxml2-dev

RUN docker-php-ext-install soap

# Copy source files
COPY src/ /var/www/html/
COPY docker-cli/init.sh /usr/local/bin/

# Set proper permissions
RUN chmod -R 777 /var/www/html && chmod +x /usr/local/bin/init.sh && touch /var/log/ddns.log && chmod 666 /var/log/ddns.log

CMD /usr/local/bin/init.sh
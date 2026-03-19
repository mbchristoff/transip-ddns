FROM python:3-slim
LABEL maintainer="MBchristoff"

ENV LANG="C.UTF-8" \
    LC_ALL="C.UTF-8"

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy source files
COPY src/ /var/www/html/
COPY docker-apache/init.sh /usr/local/bin/

# Set proper permissions
RUN chmod -R 777 /var/www/html && chmod +x /usr/local/bin/init.sh && touch /var/log/ddns.log && chmod 666 /var/log/ddns.log

EXPOSE 80

CMD /usr/local/bin/init.sh
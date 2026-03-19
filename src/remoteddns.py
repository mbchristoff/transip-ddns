#!/usr/bin/env python3
import os
from datetime import datetime

from flask import Flask, request
from transip import TransIP

app = Flask(__name__)

# Variables

# Logfile to log output to
logfile = '/var/log/ddns.log'

# The authentication key (set via REMOTEKEY environment variable)
KEY = os.environ.get('REMOTEKEY', 'Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY')  # Generate your own random key here


def log(message):
    """Append a timestamped message to the logfile."""
    time_str = datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')
    with open(logfile, 'a') as f:
        f.write(f"{time_str} {message}\r\n")


def get_transip_client():
    """Return a configured TransIP client."""
    try:
        from lib import transip_settings
        login = transip_settings.LOGIN
        private_key = transip_settings.PRIVATE_KEY
        return TransIP(login=login, private_key=private_key)
    except (ImportError, AttributeError):
        pass

    login = os.environ.get('TRANSIP_LOGIN', '')
    private_key = os.environ.get('TRANSIP_PRIVATE_KEY', '')
    private_key_file = os.environ.get('TRANSIP_PRIVATE_KEY_FILE', '')

    if not login:
        raise RuntimeError('No TransIP login configured.')
    if private_key:
        return TransIP(login=login, private_key=private_key)
    if private_key_file:
        return TransIP(login=login, private_key_file=private_key_file)
    raise RuntimeError('No private key configured.')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def remoteddns(path):
    # Get external ip address
    ip_address = request.remote_addr

    # Check for HTTP_X_FORWARDED_FOR header and use that if set
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip_address = x_forwarded_for

    # Check if domain is defined
    fqdn = request.args.get('domain')
    if not fqdn:
        return ip_address

    # Exit if the key does not match
    if request.args.get('key') != KEY:
        return 'Error, wrong key.'

    try:
        client = get_transip_client()
    except RuntimeError as e:
        return str(e)

    do_change = False
    record_found = False

    # Separate subdomain and domain from fqdn
    parts = fqdn.split('.')
    subdomain = '.'.join(parts[:-2])
    domainname = '.'.join(parts[-2:])

    # Get the current DNS entries from TransIP
    domain = client.domains.get(domainname)
    dns_entries = domain.dns.list()

    result_lines = []

    # Loop through records
    for dns_entry in dns_entries:
        # Check records for defined subdomain A record
        if dns_entry.type == 'A' and dns_entry.name == subdomain:
            # Check if the A record has to be updated
            if dns_entry.content != ip_address:
                log(f"Updating old ip {dns_entry.content}, with: {ip_address} for: {subdomain}.{domainname}.")
                result_lines.append(
                    f"Updating old ip {dns_entry.content}, with: {ip_address} "
                    f"for: {subdomain}.{domainname}"
                )
                dns_entry.content = ip_address
                do_change = True
                record_found = True
            else:
                log(f"No update required, current IP: {dns_entry.content} is unchanged for: {subdomain}.{domainname}.")
                result_lines.append(
                    f"No update required, current IP: {dns_entry.content} "
                    f"is unchanged for: {subdomain}.{domainname}"
                )
                record_found = True
            break

    if not record_found:
        result_lines.append(f"Record: {subdomain}.{domainname} not found on TransIP Nameservers.")

    # Update the record when necessary
    if do_change:
        try:
            # Commit the changes to the TransIP DNS servers
            domain.dns.replace(dns_entries)
            # Done
            result_lines.append('DNS updated successfully!')
        except Exception as e:
            # An error occurred
            result_lines.append(f'DNS not updated. {str(e)}')

    return '\n'.join(result_lines)


if __name__ == '__main__':
    # Development server only. Use Gunicorn for production:
    # gunicorn -w 4 -b 0.0.0.0:80 remoteddns:app
    app.run(host='0.0.0.0', port=80)

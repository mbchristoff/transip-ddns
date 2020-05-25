<?php
// SETTINGS
// The domain to edit
$domains []= '@.domain.tld';
$domains []= '*.domain.tld';
$domains []= 'sub.domain.tld';
$domains []= 'sub.sub.domain.tld';

// Logfile to log output to
$logfile = '/var/log/ddns.log';

// SCRIPT
// Get external ip address
$ipAddress = file_get_contents('http://ipecho.net/plain');

// Include the required files from the API
require_once('lib/Transip/DomainService.php');

if (empty($domains)) {
     exit('No domains in array' .PHP_EOL);
}

// Loop through domains
foreach ($domains as $fqdn)
{
    //set do_change to 0
    $do_change = 0;
    $record_found = 0;
    
    // Seperate subdomain and domain from fqdn
    $subdomain = implode('.', explode('.', $fqdn, -2));
    $domainname = array_slice(explode(".", $fqdn), -2)[0].".".array_slice(explode(".", $fqdn), -2)[1];
    
    // Set record that has to be changed. 
    $newValues = [
    $subdomain => $ipAddress,
    ];
    
    // Get the current DNS entries from TransIP
    $dnsEntries = Transip_DomainService::getInfo($domainname)->dnsEntries;
    
    // Loop through records
    foreach($dnsEntries as $dnsEntry)
    {
        // Check records for defined subdomain A record
        if (($dnsEntry->type == Transip_DnsEntry::TYPE_A) && ($dnsEntry->name == $subdomain))
        {
            // Check if the A record has to be updated
            if ($dnsEntry->content != $ipAddress)
            {
                $time = date('d/m/Y h:i:s a', time());
                file_put_contents($logfile, "". $time ." Updating old ip " . $dnsEntry->content . ", with: ". $ipAddress . " for: " . $subdomain . ".". $domainname . ".\r\n", FILE_APPEND);

                echo "Updating old ip " . $dnsEntry->content . ", with: ". $ipAddress . " for: " . $subdomain . ".". $domainname .PHP_EOL;
                $dnsEntry->content = $newValues[$dnsEntry->name];
                $do_change=1;
                $record_found=1;
            }
            else
            {
                $time = date('d/m/Y h:i:s a', time());
                file_put_contents($logfile, "". $time ." No update required, current IP: " . $dnsEntry->content . " is unchanged for: " . $subdomain . ".". $domainname . ".\r\n", FILE_APPEND);
                
                echo "No update required, current IP: " . $dnsEntry->content . " is unchanged for: " . $subdomain . ".". $domainname .PHP_EOL;
                $record_found=1;
            }
            break;
        }
        
    }

    if ($record_found == 0 )
    {
        echo "Record: " . $subdomain . ".". $domainname . " not found on TransIP Nameservers." .PHP_EOL;
        
    }

    // Update the record when nessecary
    if ($do_change == 1 )
    {
        try
        {
          // Commit the changes to the TransIP DNS servers
          Transip_DomainService::setDnsEntries($domainname, $dnsEntries);
          // Done
          echo 'DNS updated successfully!' .PHP_EOL;
        }
        catch(SoapFault $f)
        {
          // An error occured
          echo 'DNS not updated.' . $f->getMessage() .PHP_EOL;
        }
    }
}
?>
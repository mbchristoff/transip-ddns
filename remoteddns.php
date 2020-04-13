<?php
// Variables

// Logfile to log output to
$logfile = '/var/log/nginx/ddns/remote.log'; //Make sure the path is writable

// The authentication key
define('KEY', 'Mjs74k9bC3ACBn5pKn9eCnPeBRZFrreY'); //Generate your own random key here

// SCRIPT
// Get external ip address
$ipAddress = $_SERVER['REMOTE_ADDR'];

// Check if domain is defined
if(empty($_GET['domain']))
{
    echo $ipAddress ; exit();
}

// The domain to edit
$fqdn = $_GET['domain'];

// Exit if the key does not match
if($_GET['key'] != KEY)
{
    echo "Error, wrong key."; exit();
}

// Include the required files from the API
require_once('lib/Transip/DomainService.php');

//set do_change to 0
$do_change = 0;
    
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
        }
        else
        {
            $time = date('d/m/Y h:i:s a', time());
            file_put_contents($logfile, "". $time ." No update required, current IP: " . $dnsEntry->content . " is unchanged for: " . $subdomain . ".". $domainname . ".\r\n", FILE_APPEND);
            
            echo "No update required, current IP: " . $dnsEntry->content . " is unchanged for: " . $subdomain . ".". $domainname .PHP_EOL;
        }
        break;
    }
    
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
?>
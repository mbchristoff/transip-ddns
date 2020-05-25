<?php

/**
 * This class models a Haip
 *
 * @package Transip
 * @class Haip
 * @author TransIP (support@transip.nl)
 */
class Transip_Haip
{
	/**
	 * HA-IP name
	 *
	 * @var string
	 */
	public $name = '';

	/**
	 * HA-IP status
	 *
	 * @var string
	 */
	public $status = '';

	/**
	 * If the HA-IP is blocked
	 *
	 * @var boolean
	 */
	public $isBlocked = false;

	/**
	 * HA-IP IPv4 address
	 *
	 * @var string
	 */
	public $ipv4Address = '';

	/**
	 * HA-IP IPv6 address
	 *
	 * @var string
	 */
	public $ipv6Address = '';

	/**
	 * Name of Vps attached to the HA-IP
	 *
	 * @var string
	 */
	public $vpsName = '';

	/**
	 * IPv4 address of Vps attached to the HA-IP
	 *
	 * @var string
	 */
	public $vpsIpv4Address = '';

	/**
	 * IPv6 address of Vps attached to the HA-IP
	 *
	 * @var string
	 */
	public $vpsIpv6Address = '';
}

?>

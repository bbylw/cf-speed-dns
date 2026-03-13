#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNSPod DNS updater.
Updates DNSPod (Tencent Cloud) DNS records with the latest optimized IPs.
"""

import traceback
from typing import List, Dict, Any, Optional

import requests

from common import (
    get_env_var,
    get_cf_speed_test_ip,
    pushplus_send,
    format_current_time,
    log_success,
    log_error,
    DEFAULT_TIMEOUT,
)
from qCloud import QcloudApiv3


def build_dns_info(cloud: QcloudApiv3, domain: str, sub_domain: str) -> List[Dict[str, Any]]:
    """
    Build DNS record information from DNSPod.

    Args:
        cloud: QcloudApiv3 instance
        domain: Domain name
        sub_domain: Subdomain name

    Returns:
        List of record info dicts with 'recordId' and 'value' keys
    """
    def_info = []

    try:
        ret = cloud.get_record(domain, 100, sub_domain, "A")
        for record in ret.get("data", {}).get("records", []):
            if record.get("line") == "默认":
                def_info.append({
                    "recordId": record.get("id"),
                    "value": record.get("value")
                })
        log_success("build_info", str(def_info))
    except Exception as e:
        traceback.print_exc()
        log_error("build_info", str(e))

    return def_info


def change_dns(
    cloud: QcloudApiv3,
    domain: str,
    sub_domain: str,
    record_id: int,
    cf_ip: str
) -> str:
    """
    Update DNS record with new IP.

    Args:
        cloud: QcloudApiv3 instance
        domain: Domain name
        sub_domain: Subdomain name
        record_id: Record ID to update
        cf_ip: New IP address

    Returns:
        Status message
    """
    try:
        cloud.change_record(domain, record_id, sub_domain, cf_ip, "A", "默认", 600)
        log_success("change_dns", cf_ip)
        return f"ip:{cf_ip} 解析 {sub_domain}.{domain} 成功"
    except Exception as e:
        traceback.print_exc()
        log_error("change_dns", str(e))
        return f"ip:{cf_ip} 解析 {sub_domain}.{domain} 失败"


def main() -> None:
    """Main entry point."""
    # Load configuration
    domain = get_env_var("DOMAIN")
    sub_domain = get_env_var("SUB_DOMAIN")
    secret_id = get_env_var("SECRETID")
    secret_key = get_env_var("SECRETKEY")
    pushplus_token = get_env_var("PUSHPLUS_TOKEN")

    # Initialize DNSPod client
    cloud = QcloudApiv3(secret_id, secret_key)

    # Get existing DNS records
    dns_info = build_dns_info(cloud, domain, sub_domain)
    if not dns_info:
        log_error("build_dns_info", f"No DNS records found for {sub_domain}.{domain}")
        return

    # Fetch latest optimized IPs
    ip_addresses_str = get_cf_speed_test_ip()
    if not ip_addresses_str:
        log_error("get_cf_speed_test_ip", "Failed to fetch IP addresses")
        return

    ip_addresses = [ip.strip() for ip in ip_addresses_str.split(",") if ip.strip()]
    if not ip_addresses:
        log_error("parse_ip_addresses", "No valid IP addresses found")
        return

    # Update DNS records and collect results
    pushplus_content = []
    for index, ip_address in enumerate(ip_addresses):
        if index >= len(dns_info):
            break
        result = change_dns(
            cloud,
            domain,
            sub_domain,
            dns_info[index]["recordId"],
            ip_address
        )
        pushplus_content.append(result)

    # Send notification
    if pushplus_content:
        pushplus_send(pushplus_token, "IP优选DNSPOD推送", "\n".join(pushplus_content))


if __name__ == "__main__":
    main()

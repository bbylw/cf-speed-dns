#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tencent Cloud DNSPod API wrapper.
Provides a simplified interface to DNSPod operations using Tencent Cloud SDK.
"""

import json
from typing import Dict, Any, List

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.dnspod.v20210323 import dnspod_client, models


class QcloudApiv3:
    """
    Wrapper for Tencent Cloud DNSPod API v3.

    Provides methods to manage DNS records:
    - get_record: List DNS records
    - create_record: Create new DNS record
    - change_record: Modify existing DNS record
    - del_record: Delete DNS record
    - get_domain: Get domain information
    """

    def __init__(self, secret_id: str, secret_key: str):
        """
        Initialize with Tencent Cloud credentials.

        Args:
            secret_id: Tencent Cloud SecretId
            secret_key: Tencent Cloud SecretKey
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.cred = credential.Credential(secret_id, secret_key)

    def _create_client(self) -> dnspod_client.DnspodClient:
        """Create a new DNSPod client instance."""
        return dnspod_client.DnspodClient(self.cred, "")

    @staticmethod
    def _format_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Format a record dict to use lowercase keys and add 'id' alias."""
        new_record = {}
        for key, value in record.items():
            new_record[key.lower()] = value
        # Add 'id' as alias for 'recordid' if present
        if "recordid" in new_record:
            new_record["id"] = new_record["recordid"]
        return new_record

    @staticmethod
    def _build_empty_response(domain: str, grade: str = "DP_Free") -> Dict[str, Any]:
        """Build an empty response structure."""
        return {
            "code": 0,
            "data": {
                "records": [],
                "domain": {"grade": grade}
            }
        }

    def del_record(self, domain: str, record_id: int) -> Dict[str, Any]:
        """
        Delete a DNS record.

        Args:
            domain: Domain name
            record_id: Record ID to delete

        Returns:
            API response dict
        """
        client = self._create_client()
        req = models.DeleteRecordRequest()
        params = {"Domain": domain, "RecordId": record_id}
        req.from_json_string(json.dumps(params))

        resp = client.DeleteRecord(req)
        resp_dict = json.loads(resp.to_json_string())
        resp_dict["code"] = 0
        resp_dict["message"] = "None"
        return resp_dict

    def get_record(
        self,
        domain: str,
        length: int,
        sub_domain: str,
        record_type: str
    ) -> Dict[str, Any]:
        """
        Get DNS records for a domain.

        Args:
            domain: Domain name
            length: Maximum number of records to return
            sub_domain: Subdomain to filter by
            record_type: Record type (e.g., 'A', 'CNAME')

        Returns:
            API response dict with records
        """
        try:
            client = self._create_client()
            req = models.DescribeRecordListRequest()
            params = {
                "Domain": domain,
                "Subdomain": sub_domain,
                "RecordType": record_type,
                "Limit": length
            }
            req.from_json_string(json.dumps(params))

            resp = client.DescribeRecordList(req)
            resp_dict = json.loads(resp.to_json_string())

            # Format response
            result = self._build_empty_response(domain)
            for record in resp_dict.get("RecordList", []):
                result["data"]["records"].append(self._format_record(record))

            # Get domain grade
            domain_info = self.get_domain(domain)
            result["data"]["domain"]["grade"] = domain_info.get(
                "DomainInfo", {}
            ).get("Grade", "DP_Free")

            return result

        except TencentCloudSDKException:
            # Return empty response on SDK exception
            try:
                domain_info = self.get_domain(domain)
                grade = domain_info.get("DomainInfo", {}).get("Grade", "DP_Free")
            except Exception:
                grade = "DP_Free"
            return self._build_empty_response(domain, grade)

    def create_record(
        self,
        domain: str,
        sub_domain: str,
        value: str,
        record_type: str = "A",
        line: str = "默认",
        ttl: int = 600
    ) -> Dict[str, Any]:
        """
        Create a new DNS record.

        Args:
            domain: Domain name
            sub_domain: Subdomain name
            value: Record value (IP address)
            record_type: Record type, defaults to 'A'
            line: Record line, defaults to '默认'
            ttl: Time to live in seconds, defaults to 600

        Returns:
            API response dict
        """
        client = self._create_client()
        req = models.CreateRecordRequest()
        params = {
            "Domain": domain,
            "SubDomain": sub_domain,
            "RecordType": record_type,
            "RecordLine": line,
            "Value": value,
            "TTL": ttl
        }
        req.from_json_string(json.dumps(params))

        resp = client.CreateRecord(req)
        resp_dict = json.loads(resp.to_json_string())
        resp_dict["code"] = 0
        resp_dict["message"] = "None"
        return resp_dict

    def change_record(
        self,
        domain: str,
        record_id: int,
        sub_domain: str,
        value: str,
        record_type: str = "A",
        line: str = "默认",
        ttl: int = 600
    ) -> Dict[str, Any]:
        """
        Modify an existing DNS record.

        Args:
            domain: Domain name
            record_id: Record ID to modify
            sub_domain: Subdomain name
            value: New record value (IP address)
            record_type: Record type, defaults to 'A'
            line: Record line, defaults to '默认'
            ttl: Time to live in seconds, defaults to 600

        Returns:
            API response dict
        """
        client = self._create_client()
        req = models.ModifyRecordRequest()
        params = {
            "Domain": domain,
            "SubDomain": sub_domain,
            "RecordType": record_type,
            "RecordLine": line,
            "Value": value,
            "TTL": ttl,
            "RecordId": record_id
        }
        req.from_json_string(json.dumps(params))

        resp = client.ModifyRecord(req)
        resp_dict = json.loads(resp.to_json_string())
        resp_dict["code"] = 0
        resp_dict["message"] = "None"
        return resp_dict

    def get_domain(self, domain: str) -> Dict[str, Any]:
        """
        Get domain information.

        Args:
            domain: Domain name

        Returns:
            API response dict with domain info
        """
        client = self._create_client()
        req = models.DescribeDomainRequest()
        params = {"Domain": domain}
        req.from_json_string(json.dumps(params))

        resp = client.DescribeDomain(req)
        return json.loads(resp.to_json_string())

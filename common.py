#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common utilities for DNS updaters.
Provides shared functions for fetching IPs and sending notifications.
"""

import json
import os
import time
import traceback
from typing import Optional

import requests

# Constants
IP_TOP_URL = "https://ip.164746.xyz/ipTop.html"
PUSHPLUS_URL = "http://www.pushplus.plus/send"
DEFAULT_TIMEOUT = 10
MAX_RETRIES = 5
DEFAULT_TTL = 600


def get_env_var(name: str) -> str:
    """Get environment variable or raise error with helpful message."""
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Environment variable '{name}' is not set")
    return value


def get_cf_speed_test_ip(timeout: int = DEFAULT_TIMEOUT, max_retries: int = MAX_RETRIES) -> Optional[str]:
    """
    Fetch the latest optimized Cloudflare IPs from the service.

    Args:
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts

    Returns:
        Comma-separated IP addresses or None if all attempts fail
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(IP_TOP_URL, timeout=timeout)
            if response.status_code == 200:
                return response.text.strip()
        except Exception as e:
            traceback.print_exc()
            print(f"get_cf_speed_test_ip failed (attempt {attempt + 1}/{max_retries}): {e}")

    return None


def pushplus_send(token: str, title: str, content: str) -> None:
    """
    Send notification via PushPlus.

    Args:
        token: PushPlus API token
        title: Message title
        content: Message content (markdown format)
    """
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown",
        "channel": "wechat"
    }
    headers = {"Content-Type": "application/json"}

    try:
        requests.post(
            PUSHPLUS_URL,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            timeout=DEFAULT_TIMEOUT
        )
    except Exception as e:
        print(f"PushPlus notification failed: {e}")


def format_current_time() -> str:
    """Return formatted current time string."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def log_success(action: str, ip: str) -> str:
    """Log success message and return formatted log string."""
    message = f"{action} success: ---- Time: {format_current_time()} ---- ip: {ip}"
    print(message)
    return message


def log_error(action: str, message: str) -> str:
    """Log error message and return formatted log string."""
    error_msg = f"{action} ERROR: ---- Time: {format_current_time()} ---- MESSAGE: {message}"
    print(error_msg)
    return error_msg

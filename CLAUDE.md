# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

cf-speed-dns is a Cloudflare Speed Test DNS updater that provides optimized Cloudflare CDN IPs and automatically updates DNS records with the best performing IPs. The project uses GitHub Actions workflows to run periodically.

## Architecture

The project consists of four Python modules:

- **common.py** - Shared utilities including:
  - `get_cf_speed_test_ip()` - Fetches optimized IPs from the service
  - `pushplus_send()` - Sends PushPlus notifications
  - `get_env_var()` - Validates and retrieves environment variables
  - Logging utilities (`log_success`, `log_error`, `format_current_time`)

- **dnscf.py** - Updates Cloudflare DNS records using the Cloudflare API v4. Fetches the latest optimized IPs from `ipTop.html` and updates DNS A records for the configured domain.

- **dnspod.py** - Updates DNSPod (Tencent Cloud) DNS records using the QcloudApiv3 class. Similar functionality to dnscf.py but for DNSPod.

- **qCloud.py** - Wrapper class `QcloudApiv3` around Tencent Cloud DNSPod SDK (`tencentcloud-sdk-python`). Provides methods: `get_record`, `create_record`, `change_record`, `del_record`, `get_domain`.

## GitHub Actions Workflows

All workflows are in `.github/workflows/`:

- **sync.yml** - Syncs forks with upstream daily (only runs on forks)
- **dns_cf.yml** - Runs `dnscf.py` every 6 hours to update Cloudflare DNS
- **dns_pod.yml** - Runs `dnspod.py` every 6 hours to update DNSPod DNS

## Configuration

All scripts read configuration from environment variables:

**dnscf.py:** `CF_API_TOKEN`, `CF_ZONE_ID`, `CF_DNS_NAME`, `PUSHPLUS_TOKEN`

**dnspod.py:** `DOMAIN`, `SUB_DOMAIN`, `SECRETID`, `SECRETKEY`, `PUSHPLUS_TOKEN`

## HTML Interface

- **index.html** - Web dashboard displaying the top 10 optimized Cloudflare IPs with latency and speed metrics
- **ipTop.html** - Simple text endpoint returning the top 2 IPs (comma-separated)
- **ipTop10.html** - Simple text endpoint returning the top 10 IPs (comma-separated)

## Development

Install dependencies:
```bash
pip install -r requirements.txt
```

Run individual scripts locally (requires environment variables):
```bash
python dnscf.py
python dnspod.py
```

## Dependencies

See `requirements.txt`:
- `requests==2.28.1`
- `tencentcloud-sdk-python==3.0.806`

## Data Source

The scripts fetch optimized IPs from `https://ip.164746.xyz/ipTop.html` (hosted on GitHub Pages from this repo). The IP data is updated by an external CloudflareSpeedTest tool.

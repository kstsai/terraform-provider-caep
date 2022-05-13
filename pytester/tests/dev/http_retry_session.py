# !/usr/bin/env python
# -*-coding: utf-8 -*-
from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter
from requests_toolbelt.adapters import host_header_ssl


def retry_session(retries, session=None, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504)):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', host_header_ssl.HostHeaderSSLAdapter(max_retries=retry))
    return session

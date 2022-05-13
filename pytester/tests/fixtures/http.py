# !/usr/bin/env python
# -*-coding: utf-8 -*-
from functools import partial
import pytest
from tests.dev.http_retry_session import retry_session

@pytest.fixture
def request_session():
    yield retry_session(retries=5)


@pytest.fixture
def headers(control_name):
    return {
        "Content-Type": "application/json",
        "Connection": "close",
        "Host": control_name
    }


@pytest.fixture
def http_get(request_session, headers, root_ca_path):
    yield partial(request_session.get, headers=headers, verify=root_ca_path)


@pytest.fixture
def http_post(request_session, headers, root_ca_path):
    yield partial(request_session.post, headers=headers, verify=root_ca_path)


@pytest.fixture
def http_put(request_session, headers, root_ca_path):
    yield partial(request_session.put, headers=headers, verify=root_ca_path)


@pytest.fixture
def http_delete(request_session, headers, root_ca_path):
    yield partial(request_session.delete, headers=headers, verify=root_ca_path)

@pytest.fixture
def http_patch(request_session, headers, root_ca_path):
    yield partial(request_session.patch, headers=headers, verify=root_ca_path)

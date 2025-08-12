# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import io
import json
from overrides import overrides
import requests

from .runner import PaasRunner


COORDINATOR_URL = 'https://gitlab.test'
COORDINATOR_JOB_REQUEST_URL = 'https://gitlab.test/api/v4/jobs/request'


class FlavorForTests:
    """Mock Flavor object, with just enough info for assertions."""
    def __init__(self, weight):
        self.weight = weight


def request_recorder(records, responses):
    """Record sent requests and treat each from the given responses.

    :param responses: a list of :class:`request.Response` instances or
                      :class:`Exception` instances. In the latter case,
                      the exception is raised instead of returning the
                      response.
    :param records: list to which the recorder appends the request that is
                    being sent.
    """
    def request(meth, url, **kwargs):
        records.append((meth, url,  kwargs))
        resp = responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp

    return request


def make_response(status_code, body,
                  headers=None,
                  encoding='utf-8'):
    """Create a :class:`request.Response` instance.

    :param body: must be `bytes`.
    """
    resp = requests.models.Response()
    resp.status_code = status_code
    # force encoding as suggested in docstring of requests.models
    # because init from headers doesn't work with the way we instantiate
    # the response, leading to a detection library being used, that fires
    # a UserWarning if content is too small (facepalm unicode religion)
    resp.encoding = encoding
    resp.raw = io.BytesIO(body)
    if headers is not None:
        resp.headers = headers
    return resp


def make_json_response(obj, status_code=200, headers=None):
    return make_response(status_code, json.dumps(obj).encode(),
                         headers=headers)


class PaasResource():
    def __init__(self, rsc_id, credentials):
        self.id = rsc_id
        self.credentials = credentials
        self.launch_errors = {}  # job_id -> PaasResourceError

    def dump(self):
        """Like real-workd PAAS resources, we don't include credentials."""
        return self.id

    def launch(self, job_data):
        err = self.launch_errors.get(job_data['id'])
        if err is not None:
            raise err


class RunnerForTests(PaasRunner):

    paas_credentials = None

    def inner_executor(self):
        return 'docker'

    def is_config_item_for_inner(self, key):
        return not key.startswith('priv_')

    def paas_resource(self, rsc_id):
        return PaasResource(rsc_id, self.paas_credentials)

    @overrides
    def load_paas_resource(self, data):
        return PaasResource(data, self.paas_credentials)


RunnerForTests.register()

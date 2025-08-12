# Copyright 2025 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import logging
import requests
import secrets
import string
import time
import toml
from urllib.parse import quote as urlquote

import grpc

from .exceptions import (
    JobLaunchTimeout,
    PaasResourceError,
)
from .grpc.heptapod_paas_runner_pb2 import (
    Job,
    CanTakeJobRequest,
    LaunchJobRequest,
)
from .grpc.heptapod_paas_runner_pb2_grpc import PAASResourceRunnerStub

from overrides import overrides

logger = logging.getLogger(__name__)

TOKEN_ALPHABET = string.ascii_letters + string.digits


class PaasResource:
    service_based = False

    def finished_standby_seconds(self):
        return 0

    def log_fmt(self):
        """String representation useful for debug logs.

        In particular, it is useful not to include redundant or sensitive
        attributes or fields:
        """
        return f'{self.__class__.__name__}({self.app_id!r})'

    def dump(self):
        """Serialization for state persistence."""
        raise NotImplementedError("dump")  # pragma no cover


class PaasHelperServiceResource(PaasResource):
    """Common logic for all resources running the PAAS Runner helper service.
    """

    service_based = True

    netloc = None
    """The network location where the service listens to (HOST:PORT).

    To be initialized by subclasses.
    """

    paas_token = None
    """The token to use for authentication to Heptapod PAAS Runner helper."""

    service_tls = True
    """Whether to use TLS for the gRPC channel."""

    can_take_job_delay = 1
    """Time in seconds to wait between calling `CanTakeJob` again."""

    can_take_job_timeout = 10

    max_launch_retry_wait = 5
    """Maximum time in seconds to wait after launch gave HTTP/1 503."""

    http1 = False
    """Whether to use REST over HTTP/1.1 rather than gRPC (HTTP/2)"""

    grpc = True

    def init_common(self, runner, app_id, netloc):
        self.app_id = app_id
        self.netloc = netloc
        self.app_id = app_id
        self.launched = False
        self.runner_name = runner.unique_name
        self.standby_seconds_once_finished = runner.config.get(
            'paas_keep_resources_for_reuse_seconds', 120)
        self.config = runner.inner_config()

    def init_paas_token(self):
        if self.paas_token is None:
            self.paas_token = ''.join(secrets.choice(TOKEN_ALPHABET)
                                      for i in range(40))

    def init_grpc(self, runner, app_id, netloc):
        self.init_common(runner, app_id, netloc)
        if self.service_tls:  # pragma no cover
            # TODO create token at provisioning, pass it down to the service
            # startup, and implement basic auth
            # (necessary for production anywhere)
            # see https://github.com/grpc/grpc/blob/master/examples/
            #           python/auth/token_based_auth_client.py
            self.channel = grpc.secure_channel(
                netloc,
                grpc.ssl_channel_credentials()
            )
        else:
            self.channel = grpc.insecure_channel(netloc)
        self.service = PAASResourceRunnerStub(self.channel)

    def init_http1(self, runner, app_id, netloc):
        self.init_common(runner, app_id, netloc)
        self.http1 = True
        self.grpc = False

        scheme = 'https' if self.service_tls else 'http'
        self.http1_url = '://'.join((scheme, netloc))
        self.service_headers = {'Authorization': f'Bearer {self.paas_token}'}

    @overrides
    def dump(self):
        # runner's host may change, but an existing resource has a given
        # host and must still be trackable / decommissioned etc.
        return dict(app_id=self.app_id,
                    netloc=self.netloc,
                    paas_token=self.paas_token)

    def can_take_job(self):
        try:
            if self.http1:
                return self.http1_can_take_job()
            return self.service.CanTakeJob(CanTakeJobRequest()).can_take_job
        except Exception as exc:
            logger.info("Resource cannot take job (yet): %r", exc)
            return False

    def wait_can_take_job(self, interruptible_sleep):
        """Wait for the resource to be able to take jobs

        :returns: ``True`` if a trace not written by this process
            has been detected, ``False`` if sleep between polling requests
            was interrupted.
        :raises: JobLaunchTimeout in case of timeout
        """
        start = time.time()
        timeout = self.can_take_job_timeout
        while not self.can_take_job():
            now = time.time()
            if now - start > timeout:
                raise JobLaunchTimeout(None, timeout)
            if interruptible_sleep(self.can_take_job_delay):
                return False
        return True

    def http1_can_take_job(self):
        resp = requests.get(self.http1_url + '/can-take-job',
                            headers=self.service_headers)
        if resp.status_code >= 400:
            return False
        return resp.json()

    def launch(self, job_data):
        if self.http1:
            return self.http1_launch(job_data)

        grpc_job = Job(job_id=job_data['id'],
                       runner_name=self.runner_name)

        job_json = json.dumps(job_data)
        self.service.LaunchJob(LaunchJobRequest(
            job=grpc_job,
            specification=job_json,
            config=toml.dumps(self.config),
        ))
        self.launched = True

    def http1_launch_error(self, resp):
        return PaasResourceError(
                self.app_id, 'service-docker', 'launch', resp.status_code,
                error_details=resp.text
            )

    def http1_launch(self, job_data, retry_count=0):
        job_json = json.dumps(job_data)
        resp = requests.post(self.http1_url + '/launch-job',
                             headers=self.service_headers,
                             json=dict(job_id=job_data['id'],
                                       runner_name=self.runner_name,
                                       specification=job_json,
                                       config=toml.dumps(self.config))
                             )
        if resp.status_code == 503:
            if retry_count >= 1:
                raise self.http1_launch_error(resp)
            # probably the resource is being decommissioned, but it could
            # be something else. As this is called from the main polling
            # loop, we cannot aford to wait for a long time.
            retry = resp.headers.get('Retry-After')
            if retry is None:
                retry = self.max_launch_retry_wait
            else:
                try:
                    retry = float(retry.strip())
                except ValueError:
                    retry = self.max_launch_retry_wait
            retry = min(self.max_launch_retry_wait, retry)
            time.sleep(retry)
            return self.http1_launch(job_data, retry_count=retry_count + 1)
        if resp.status_code != 201:
            raise self.http1_launch_error(resp)
        self.launched = True

    def is_finished(self, job_handle):
        if self.http1:
            job_url = '/'.join(
                (self.http1_url,
                 urlquote(self.runner_name),
                 str(job_handle.job_id))
            )
            resp = requests.get(job_url, headers=self.service_headers)

            if resp.status_code != 200:
                raise PaasResourceError(
                    self.app_id, 'service-docker', 'is_finished',
                    resp.status_code,
                    error_details=resp.text)
            resp = resp.json()
            running, exit_code = resp['running'], resp['exit_code']
        else:
            grpc_job = job_handle.as_grpc()
            status = self.service.JobStatus(grpc_job)
            running, exit_code = status.running, status.exit_code

        if running:
            return False

        if exit_code != 0:
            logger.warning("%s exited with code %d", job_handle, exit_code)

        # now that the PAAS Runner nows the job is finished, the helper
        # service can forget about it, so that it can claim to be able to
        # take another job.
        if self.http1:
            resp = requests.delete(job_url, headers=self.service_headers)
            if resp.status_code >= 400:
                raise PaasResourceError(
                    self.app_id, 'service-docker', 'forget_job',
                    resp.status_code,
                    error_details=resp.text)
        else:
            self.service.ForgetJob(grpc_job)
        return True

    def finished_standby_seconds(self):
        return self.standby_seconds_once_finished

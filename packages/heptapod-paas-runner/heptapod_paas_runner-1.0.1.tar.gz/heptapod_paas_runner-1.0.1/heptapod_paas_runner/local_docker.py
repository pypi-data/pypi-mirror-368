# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import os
from overrides import overrides
from urllib.parse import urlparse
import subprocess
import tempfile

from .docker import DockerBuildHelper
from .exceptions import (
    PaasResourceError,
)
from .paas_resource import PaasResource
from .runner import PaasRunner
from .testing import FlavorForTests

# same environment variable supported by the Docker executor, see
# https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section
DEFAULT_DOCKER_URL = os.environ.get('DOCKER_HOST',
                                    'unix:///var/run/docker.sock')


class LocalDockerRunner(PaasRunner):

    executor = 'local-docker'
    available_flavors = {'M': FlavorForTests(1)}

    def __init__(self, config):
        super(LocalDockerRunner, self).__init__(config)

        docker_raw_url = self.config.get('host', DEFAULT_DOCKER_URL)
        docker_url = urlparse(docker_raw_url)
        if docker_url.scheme != 'unix':
            raise ValueError("Runner %r (executor %r) invalid Docker host "
                             "URL %r: only Unix Domain sockets "
                             "(unix:///some/path.socket) are supported " % (
                                 self.unique_name, self.executor,
                                 docker_raw_url))
        self.docker_socket = docker_url.path

    @overrides
    def inner_executor(self):
        return 'docker'

    @overrides
    def is_config_item_for_inner(self, key):
        """All config parameters except `host` are standard.

        `host`, the Docker endpoint URL is meaningful for the dispatcher only,
        and is mounted at a fixed place for the inner executor.
        """
        return key != 'host'

    @overrides
    def provision(self, job):
        app_id = 'hpd-job-%s-%d' % (self.unique_name.lower(), job['id'])
        return LocalDockerApplication(app_id)

    @overrides
    def load_paas_resource(self, data):
        return LocalDockerApplication(data)

    @overrides
    def launch(self, paas_resource, job_data):
        """Build the image and run the job, like an actual PAAS runner would.

        TODO avoid subprocess, and use the docker Python lib, so that this
        method becomes testable (if only with severe mocking, but at least
        could catch some discrepancies on our side).
        """
        docker_image = paas_resource.docker_image
        try:
            with tempfile.TemporaryDirectory() as tmp_path:
                build_helper = DockerBuildHelper.from_runner_config(
                    tmp_path, self.config)
                build_helper.write_build_context(self, job_data)
                subprocess.check_call(("docker", "build",
                                       '-t', docker_image,
                                       tmp_path))

                subprocess.check_call(
                    ("docker", "run",
                     '--rm', '-t',
                     '-v', self.docker_socket + ':/var/run/docker.sock',
                     docker_image))
        except Exception as exc:
            raise PaasResourceError(executor=self.executor,
                                    action='launch',
                                    resource_id=paas_resource.app_id,
                                    code=None,
                                    error_details=repr(exc),
                                    )

    @overrides
    def decommission(self, paas_resource):
        subprocess.check_call(('docker', 'rmi', paas_resource.docker_image))


LocalDockerRunner.register()


class LocalDockerApplication(PaasResource):

    def __init__(self, app_id):
        """By convention, the application is the Docker image."""
        self.app_id = self.docker_image = app_id

    @overrides
    def dump(self):
        return self.app_id

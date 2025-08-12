# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
from overrides import overrides
import requests
import tempfile
import time

from .docker import DockerBuildHelper
from .exceptions import (
    DeploymentBranchAlreadyExisting,
    GitLabUnexpectedError,
    PaasProvisioningError,
    PaasResourceError,
)
from .job import get_job_variable
from .paas_resource import (
    PaasResource,
    PaasHelperServiceResource,
)
from .runner import PaasRunner
from .util import retry

logger = logging.getLogger(__name__)

FLAVOR_JOB_VARIABLE_NAME = 'CI_CLEVER_CLOUD_FLAVOR'
DEFAULT_FLAVOR = 'M'
"""Ultimate default if flavor not specified in job nor runner config."""

CC_ORGA_ID_ATTRIBUTE = 'cc_orga_id'
CC_ORGA_TOKEN_ATTRIBUTE = 'cc_orga_token'

CC_API_RETRY_DELAY_SECONDS = 2


def convert_http_error(http_response):
    """Return error code, message."""
    try:
        resp_data = http_response.json()
        assert resp_data['type'] == 'error'
        # checked with Clever, `id` is definitely an error code
        return resp_data['id'], resp_data['message']
    except Exception:
        return None, http_response.text


class CleverCloudApplication(PaasResource):

    def __init__(self, orga, app_id, deploy_url, user, password,
                 launched=False,
                 weight=None,
                 **kw,
                 ):
        self.orga = orga
        self.app_id = app_id
        self.api_url = orga.app_url(self.app_id)
        self.deploy_url = deploy_url

        self.git_push_url = deploy_url.replace(
            'https://',
            'https://%s:%s@' % (user, password))
        self.weight = weight
        self.launched = launched

    @property
    def executor(self):
        return self.orga.executor

    @property
    def headers(self):
        return self.orga.headers

    @overrides
    def dump(self):
        # we don't dump CC API credentials. If this is loaded by a Runner,
        # it will reinitialize the credentials, maybe with an updated value.
        return dict(id=self.app_id,
                    gitlab_namespace=self.orga.gitlab_namespace,
                    weight=self.weight,
                    launched=self.launched,
                    deploy_url=self.deploy_url)

    @overrides
    def log_fmt(self):
        """String representation useful for debug logs.

        Not included attributes or fields:

        - :attr:`deploy_url`: can be found by requesting the CC API if needed.
        - :attr:`gitlab_namespace`: can be found by looking at the job in the
          GitLab UI (or API)
        """
        return (f'CleverCloudApplication(app_id={self.app_id!r}, '
                f'weight={self.weight:.2f}, '
                f'launched={self.launched})')

    def get_info(self):
        resp = requests.get(self.api_url,
                            headers=self.headers)
        if resp.status_code >= 400:
            error_code, message = convert_http_error(resp)
            raise PaasResourceError(self.app_id, self.executor,
                                    action='get-info',
                                    action_details=None,
                                    code=error_code,
                                    transport_code=resp.status_code,
                                    error_details=message)
        return resp.json()

    def put_env(self, env):
        """Add environment variables to the application.
        """
        resp = requests.put(self.api_url + '/env',
                            json=env,
                            headers=self.headers)

        if resp.status_code >= 400:
            error_code, message = convert_http_error(resp)
            raise PaasResourceError(self.app_id, self.executor,
                                    action='put-env',
                                    action_details=env,
                                    code=error_code,
                                    transport_code=resp.status_code,
                                    error_details=message)
        # success code should be 328.
        logger.debug('CleverCloudApplication.put_env: successful response %r',
                     resp.text)
        return resp


class CleverCloudDockerRunner(PaasRunner):

    executor = 'clever-docker'
    cc_app_class = CleverCloudApplication
    _available_flavors = (None, None)
    """dict of available flavors and timestamp of retrieval.
    """

    def __init__(self, config):
        super(CleverCloudDockerRunner, self).__init__(config)
        self.init_cc_global()
        self.init_cc_git()
        self.init_cc_orga()
        self.init_common_app_params()

    def init_cc_global(self):
        self.cc_base_url = self.config.get('cc_api_url',
                                           'https://api.clever-cloud.com/v2')
        self.cc_zone = self.config.get('cc_zone', 'par')
        self.cc_default_flavor = self.config.get('cc_default_flavor',
                                                 DEFAULT_FLAVOR)
        self.cc_max_flavor = self.config.get('cc_max_flavor')
        # TODO validate early the existence of the max flavor
        # what if it disappears afterwards?

        self.deployment_repo_timeout = self.config.get(
            'cc_deployment_repo_timeout', 20)
        self.deployment_repo_wait_step = self.config.get(
            'cc_deployment_repo_wait_step', 2)

    def init_cc_orga(self):
        if self.config.get('cc_multi_tenant'):
            self.fixed_cc_orga = None
        else:
            self.fixed_cc_orga = CleverCloudOrganization(
                self.cc_base_url,
                orga_id=self.config['cc_orga_id'],
                git_user=self.cc_git_user,
                token=self.config['cc_token'])
        self.gl_attributes_token = self.config.get(
            'cc_gitlab_namespace_attributes_token')
        self.cc_orga_id_attribute = self.config.get(
            'cc_orga_id_attribute', CC_ORGA_ID_ATTRIBUTE)
        self.cc_orga_token_attribute = self.config.get(
            'cc_orga_token_attribute', CC_ORGA_TOKEN_ATTRIBUTE)
        self.all_cc_orga_attributes = (self.cc_orga_id_attribute,
                                       self.cc_orga_token_attribute,
                                       )

    @property
    @retry(attempts=3, delay_seconds=CC_API_RETRY_DELAY_SECONDS)
    def available_flavors(self):
        """Cached dict of available flavors.

        This is a mapping whose keys are user flavor names, such as `'XL'`
        and values are :class:`CleverCloudFlavor` instances

        The caching is not really thread-safe, but the worst that can
        happen is several GET requests towards the Clever API if several
        threads realize that the timestamp is outdated at the same time.
        It is very unlikely that these requests would give different results
        and even more unlikely that it would make a difference for the end
        user (using a flavor that just got advertised or that doesn't exist
        anymore. In the first case, the job will be able to run earlier than
        expected, in the second case we're only losing a job that would have
        been invalid mere seconds later).
        """
        available, ts = self._available_flavors
        if available is not None and time.time() - ts < 3600:
            return available

        timestamp = time.time()
        # default values should be the final ones in production,
        # configurability will help us in particular to prototype with
        # the Jenkins flavors.
        flavor_context = self.config.get('cc_flavor_context',
                                         'heptapod-runner')
        params = dict(context=flavor_context)
        resp = requests.get(self.cc_base_url + '/products/flavors',
                            params=params)

        if resp.status_code >= 400:
            # TODO surely this must most of the times
            # be a transient failure. Retry logic?
            error_code, message = convert_http_error(resp)
            raise PaasProvisioningError(action='get-available-flavors',
                                        action_details=params,
                                        transport_code=resp.status_code,
                                        code=error_code,
                                        error_details=message,
                                        executor=self.executor)

        prefix = self.config.get('cc_flavor_name_prefix', flavor_context + '-')
        available = {
            flav['name'][len(prefix):]: CleverCloudFlavor(flav)
            for flav in resp.json()
            if flav['name'].startswith(prefix) and flav['available']}
        logger.info("Retrieved variant flavors. Resulting mapping: %r",
                    available)
        self._available_flavors = available, timestamp
        return available

    @property
    def min_requestable_weight(self):
        if self.cc_max_flavor is not None:
            return self.available_flavors[self.cc_max_flavor].weight

        return max(fl.weight for fl in self.available_flavors.values())

    def init_cc_git(self):
        self.cc_git_user = self.config.get('cc_auth_user', 'Jenkins')

    def init_common_app_params(self):
        self.common_app_params = {
            # TODO could depend on job rather than runner
            'zone': self.cc_zone,
            'instanceLifetime': 'TASK',
            'instanceType': 'docker',
            'deploy': 'git',
            'instanceVariant': self.config.get(
                'cc_instance_variant_uuid',
                # This is the initial UUID for Heptapod Runner variant
                "70d676a0-a775-4dc9-a43d-3121036e8515"),
            'maxInstances': 1,  # we'll do our own auto scaling
            'minInstances': 1,
        }

    def inner_executor(self):
        return 'docker'

    def is_config_item_for_inner(self, key):
        return (key != 'heptapod_runner_main_image'
                and not key.startswith('cc_'))

    @retry(attempts=3, delay_seconds=CC_API_RETRY_DELAY_SECONDS)
    def cc_docker_instance_type(self):
        """Retrieve the CC instance type that we'll be using, with details.

        The version is crucial, as we need to specify a supported one upon
        provisioning. See also #37 about caching.
        """
        resp = requests.get(self.cc_base_url + '/products/instances')
        if resp.status_code >= 400:
            error_code, message = convert_http_error(resp)
            raise PaasProvisioningError(action='get-instance-type',
                                        transport_code=resp.status_code,
                                        code=error_code,
                                        error_details=message,
                                        executor=self.executor)

        assert resp.status_code == 200
        docker_types = [inst for inst in resp.json()
                        if inst['name'] == 'Docker']
        # TODO what if several match? Are, e.g., several versions
        # possible at a given time?
        return docker_types[0]

    def cc_select_flavor(self, instance_type, job, check_max=True):
        flavor = get_job_variable(job, FLAVOR_JOB_VARIABLE_NAME)
        if flavor is None:
            flavor = self.cc_default_flavor

        available = self.available_flavors
        cc_flavor = available.get(flavor)
        if cc_flavor is None:
            raise PaasProvisioningError(
                action='check-flavor',
                transport_code=None,
                code=1,
                error_details="Selected flavor %r is not available, "
                "possible choices are %r" % (flavor,
                                             list(self.available_flavors)),
                executor=self.executor,
            )
        if check_max and self.cc_max_flavor is not None:
            max_flavor = self.available_flavors[self.cc_max_flavor]
            if cc_flavor.weight > max_flavor.weight:
                raise PaasProvisioningError(
                    action='check-flavor',
                    transport_code=None,
                    code=2,
                    error_details=f"Flavor size exceeded: this runner is "
                    f"configured to have a maximum Clever Cloud flavor of "
                    f"'{self.cc_max_flavor}', but this job specifies "
                    f"the bigger flavor '{flavor}'. Please change the value "
                    f"of the {FLAVOR_JOB_VARIABLE_NAME} job variable or "
                    f"select another runner if possible.",
                    executor=self.executor,
                )

        return cc_flavor

    def job_cc_orga(self, job):
        orga = self.fixed_cc_orga
        if orga is not None:
            return orga

        return self.cc_orga(self.gitlab_job_top_namespace(job))

    def gitlab_job_top_namespace(self, job):
        return get_job_variable(job, 'CI_PROJECT_ROOT_NAMESPACE')

    def cc_orga(self, gitlab_namespace):
        orga = self.fixed_cc_orga
        if orga is not None:
            return orga

        # perhaps we should have a dedicated PaasAccessError
        # meanwhile, this will be good enough.
        try:
            attrs = self.gitlab_custom_attributes(
                gitlab_namespace,
                self.all_cc_orga_attributes,
                token=self.gl_attributes_token,
            )
        except GitLabUnexpectedError as exc:
            raise PaasProvisioningError(
                executor=self.executor,
                action='find-orga',
                action_details='namespace=%r, '
                'failed attributes request on %r: %s' % (
                    gitlab_namespace,
                    exc.url,
                    exc.message
                ),
                code=exc.status_code)
        try:
            orga_id, orga_token = (attrs[self.cc_orga_id_attribute],
                                   attrs[self.cc_orga_token_attribute])
        except KeyError as exc:
            raise PaasProvisioningError(
                executor=self.executor,
                action='find-orga',
                action_details='namespace=%r, '
                'missing attribute %r' % (gitlab_namespace,
                                          exc.args[0]),
                code=None)

        return CleverCloudOrganization(
            self.cc_base_url,
            gitlab_namespace=gitlab_namespace,
            orga_id=orga_id,
            git_user=self.cc_git_user,
            token=orga_token)

    @overrides
    def provision(self, job):
        # TODO cache instance_type, and reload only if provision ends
        # with errors possibly due to outdated information (including change
        # of flavor availability)
        # (error code for unknown application should be 4004)
        instance_type = self.cc_docker_instance_type()

        req_data = self.common_app_params.copy()
        req_data['instanceVersion'] = instance_type['version']

        flavor = self.cc_select_flavor(instance_type, job)
        req_data['minFlavor'] = req_data['maxFlavor'] = flavor.api_name

        req_data['name'] = 'hpd-job-%s-%d' % (self.unique_name, job['id'])
        app = self.job_cc_orga(job).create_app(self, req_data)

        cc_env = {'CC_MOUNT_DOCKER_SOCKET': 'true'}
        extra_env = self.config.get('cc_extra_env')
        if extra_env:
            cc_env.update(extra_env)

        paas_token = getattr(app, 'paas_token', None)
        if paas_token is not None:
            cc_env['HEPTAPOD_PAAS_RUNNER_TOKEN'] = paas_token

        app.put_env(cc_env)
        return app

    @overrides
    def expected_weight(self, job):
        # TODO find a way to cache this call (with proper invalidation):
        instance_type = self.cc_docker_instance_type()
        # we'll let the launching thread check the max flavor and
        # provide end-user feedback.
        flavor = self.cc_select_flavor(instance_type, job, check_max=False)
        return flavor.weight

    @overrides
    def load_paas_resource(self, data):
        # this maintains compatibility with data dumped without a
        # GitLab namespace for runners with a fixed CC Organization
        gl_namespace = data.get('gitlab_namespace')
        try:
            cc_orga = self.cc_orga(gl_namespace)
        except PaasProvisioningError as exc:
            # In a multi-tenant system, one misconfigured tenant
            # should not crash the whole system.
            logger.error(
                "Failed to load PAAS resource from data %r."
                "Operations on resource, notably decommission, "
                "won't be possible. "
                "action=%r, action_details=%r, code=%r, error_details=%r",
                data, exc.action, exc.action_details,
                exc.code, exc.error_details)
            # we should also not lose data about the resource just
            # because we couldn't resolve the orga this time
            cc_orga = OrganizationNotFound(gl_namespace)

        return cc_orga.load_application(self, data)

    def wait_deployability(self, app):
        app_id = app.app_id
        wait_step = self.deployment_repo_wait_step
        timeout = self.deployment_repo_timeout

        start = time.time()
        while (time.time() - start) < timeout:
            try:
                state = app.get_info()['deployment']['repoState']
            except KeyError:
                raise PaasResourceError(
                    app_id, self.executor,
                    action='wait-deployability',
                    error_details=f"Clever Cloud Application {app_id}: "
                    "deployment details schema not understood",
                    code=3,
                    transport_code=None,
                )
            if state == 'CREATED':
                break
            time.sleep(wait_step)
        else:
            raise PaasResourceError(
                app_id, self.executor,
                action='wait-git',
                error_details='Clever Cloud Application '
                f'{app_id}: not deployable after {timeout} seconds',
                code=4,
                transport_code=None
            )

    @overrides
    def launch(self, paas_resource, job_data):
        self.wait_deployability(paas_resource)

        with tempfile.TemporaryDirectory() as tmp_path:
            build_helper = DockerBuildHelper.from_runner_config(tmp_path,
                                                                self.config)
            build_helper.write_build_context(self, job_data)
            try:
                out_err = build_helper.git_push(paas_resource.git_push_url)
            except DeploymentBranchAlreadyExisting:
                logger.warning(
                    "%s: depoyment branch already existing on remote. "
                    "There probably was an issue with state loading "
                    "or shutdown (SIGKILL or bug in shutdown sequence)",
                    paas_resource.log_fmt()
                )
            else:
                logger.debug('%s: deployment by Git push to %r done. '
                             'git subprocess stdout/stderr: %r',
                             paas_resource.log_fmt(),
                             paas_resource.deploy_url,
                             out_err)

        paas_resource.launched = True

    @overrides
    def decommission(self, paas_resource):
        app_id = paas_resource.app_id

        resp = paas_resource.orga.delete_app(app_id)
        if resp.status_code == 404:
            logger.warning("decommision: application %r is already "
                           "not present, nothing to be done", app_id)
            return False

        if resp.status_code >= 400:
            error_code, message = convert_http_error(resp)
            raise PaasResourceError(app_id, self.executor,
                                    action='delete',
                                    action_details=None,
                                    code=error_code,
                                    transport_code=resp.status_code,
                                    error_details=message)
        logger.debug('decommission: successful response %r', resp.text)
        return True

    def decommission_all(self, gitlab_namespace=None):
        """Decommission all PAAS resources for this runner.

        This is obviously dangerous and if ever exposed to the CLI or
        users in any way, care must be taken to make sure it can't
        happen by accident.

        :param gitlab_namespace: if specified, will be used to
           find the relevant Organization. Otherwise, :attr:`fixed_cc_orga`
           will be used. If the latter is ``None`` (typically case of a
           multi-tenant Runner), then `ValueError` is raised.

        :returns: the number of decommissionned resources and number of
           ignored ones (not related to this runner).
        """
        if gitlab_namespace is None:
            if self.fixed_cc_orga is None:
                raise ValueError("This Runner %r does not have a fixed "
                                 "Clever Cloud Organization. "
                                 "To decommission all "
                                 "its resources, the path of the GitLab "
                                 "namespace bearing the CC Organization and "
                                 "token must be given." % self.unique_name)
            else:
                cc_orga = self.fixed_cc_orga
        else:
            cc_orga = self.cc_orga(gitlab_namespace)

        logger.warning("Decommissionning all PAAS resources for runner %r"
                       " on Clever Cloud Organization %r",
                       self.unique_name, cc_orga.orga_id)
        rsc_name_prefix = 'hpd-job-%s-' % self.unique_name
        done = 0
        ignored = 0
        for app_data in cc_orga.list_applications():
            if not app_data.get('name', '').startswith(rsc_name_prefix):
                ignored += 1
                continue

            app = cc_orga.application(self, app_data)
            logger.info("Decommissioning app name=%r", app_data['name'])
            self.decommission(app)
            time.sleep(10)
            done += 1

        logger.info("Decommissionned the %d applications spawned by "
                    "runner %r, and ignored %d unrelated applications "
                    "in the same organization %r",
                    done, self.unique_name, ignored, cc_orga.orga_id)
        return done, ignored


CleverCloudDockerRunner.register()


class CleverCloudOrganization:

    executor = CleverCloudDockerRunner.executor
    """Used in logging and raising of exceptions."""

    transitional_default_weight = 32768
    """Weight to attribute to applications created before weight tracking.

    This is a worst-case value, meant to avoid over-provisionning due
    to underestimation of currently running jobs at the first restart
    with the weighted quota system.

    We could do better than that, by querying actual flavors in service
    upon state load, but it isn't worth the effort at this point: all we'll
    have if there are lots of running jobs is a temporary saturation, until
    at least one finishes.
    """

    def __init__(self, base_api_url, orga_id, token, git_user,
                 gitlab_namespace=None):
        """Information needed to work on Clever API for an Organization.
        """
        self.base_api_url = base_api_url
        self.orga_id = orga_id
        self.git_user = git_user
        self.token = token
        self.gitlab_namespace = gitlab_namespace

        self.url = '/'.join((base_api_url, 'organisations', orga_id))
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'token ' + self.token,
        }

    @property
    def applications_url(self):
        return '/'.join((self.url, 'applications'))

    def app_url(self, app_id):
        return '/'.join((self.applications_url, app_id))

    def create_app(self, runner, data):
        """Create an application by calling the proper endpoint.

        :returns: :class:`CleverCloudApplication`
        """
        logger.debug("create_app data=%r", data)
        resp = requests.post(self.applications_url,
                             headers=self.headers,
                             json=data)
        if resp.status_code >= 400:
            # TODO catch error due to outdated version to recompute it
            # and raise something appropriate for other errors.
            # Actual error got due to lack of version is currently in use in
            # test_clever.py for easy reference.
            error_code, message = convert_http_error(resp)
            raise PaasProvisioningError(action='create-app',
                                        action_details=data,
                                        code=error_code,
                                        transport_code=resp.status_code,
                                        error_details=message,
                                        executor=self.executor,
                                        )
        logger.debug("CleverCloud application creation: "
                     "successful response %r", resp.text)

        return self.application(runner, resp.json())

    def application(self, runner, resp_data):
        """Represent an existing CC application from API response data.

        The data can be obtained, e.g., from a creation request, or a listing
        request.
        """
        return runner.cc_app_class(
            runner=runner,
            orga=self,
            app_id=resp_data['id'],
            deploy_url=resp_data['deployment']['httpUrl'],
            user=self.git_user,
            password=self.token,
            weight=CleverCloudFlavor(resp_data['instance']['maxFlavor']).weight
        )

    def load_application(self, runner, data):
        """Load application from saved data."""
        merged = dict(
            runner=runner,
            orga=self,
            app_id=data['id'],
            deploy_url=data['deploy_url'],
            user=self.git_user,
            launched=data['launched'],
            password=self.token,
            weight=data.get('weight', self.transitional_default_weight),
        )
        paas_token = data.get('paas_token')
        if paas_token is not None:
            merged['paas_token'] = paas_token
        return runner.cc_app_class(**merged)

    def delete_app(self, app_id):
        """Delete an application.

        Kept as a method on the organization, because we need less
        detailed information to delete an application than to use it.
        """
        return requests.delete(self.app_url(app_id),
                               headers=self.headers)

    def list_applications(self):
        """Return the list of all applications.

        This list may include applications that are *not* related to
        a given Runner, or not even CI related: this is the Clever Cloud
        API request result after JSON decoding.
        """
        return requests.get(self.applications_url,
                            headers=self.headers).json()


class OrganizationNotFound(CleverCloudOrganization):
    """Represent a failure to resolve an organization.

    Used to keep track of CleverCloudApplication instances even if
    the corresponding organization could not be resolved (typically after
    a restart on a wrong configuration or while the coordinator is down).
    This is enough to allow various kinds of retry.
    """

    def __init__(self, gitlab_namespace):
        self.gitlab_namespace = gitlab_namespace
        self.git_user = None
        self.token = None
        self.url = None

    def __eq__(self, other):
        return self.gitlab_namespace == other.gitlab_namespace

    def app_url(self, app_id):
        """Always return None to express URL is not known."""

    def delete_app(self, app_id):
        raise PaasResourceError(
            app_id, self.executor,
            action='delete',
            code=22,  # chosen arbitrarily (randint call)
            error_details="Could not find Clever Cloud Organization "
            "credentials for the GitLab namespace %r this resource is "
            "linked to. Earlier logs may have details "
            "about failed attempts." % self.gitlab_namespace,
            )


class CleverCloudHelperServiceApplication(PaasHelperServiceResource,
                                          CleverCloudApplication):
    service_tls = True
    can_take_job_delay = 20
    can_take_job_timeout = 600

    def __init__(self, runner, orga, app_id, *a, paas_token=None, **kw):
        CleverCloudApplication.__init__(self, orga, app_id, *a, **kw)
        self.paas_token = paas_token
        self.init_paas_token()
        self.runner = runner
        self.init_cleverapps()

    def init_cleverapps(self):
        netloc = self.app_id.replace('_', '-') + '.cleverapps.io'
        self.init_http1(self.runner, self.app_id, netloc)

    @overrides
    def dump(self):
        # we don't dump CC API credentials. If this is loaded by a Runner,
        # it will reinitialize the credentials, maybe with an updated value.
        return dict(id=self.app_id,
                    gitlab_namespace=self.orga.gitlab_namespace,
                    weight=self.weight,
                    launched=self.launched,
                    netloc=self.netloc,
                    paas_token=self.paas_token,
                    deploy_url=self.deploy_url)


class CleverCloudHelperServiceRunner(CleverCloudDockerRunner):
    """Variant using the heptapod-paas-runner-helper service.

    Once ready, this will eventually replace CleverCloudDockerRunner.
    """
    executor = 'clever-service-docker'
    cc_app_class = CleverCloudHelperServiceApplication

    def init_common_app_params(self):
        CleverCloudDockerRunner.init_common_app_params(self)
        del self.common_app_params['instanceLifetime']

    @overrides
    def provision(self, job):
        app = CleverCloudDockerRunner.provision(self, job)
        self.start_helper_service(app)
        return app

    def start_helper_service(self, paas_resource):
        self.wait_deployability(paas_resource)

        with tempfile.TemporaryDirectory() as tmp_path:
            build_helper = DockerBuildHelper.from_runner_config(tmp_path,
                                                                self.config)
            build_helper.write_service_build_context()
            try:
                out_err = build_helper.git_push(paas_resource.git_push_url)
            except DeploymentBranchAlreadyExisting:
                logger.warning(
                    "%s: depoyment branch already existing on remote. "
                    "There probably was an issue with state loading "
                    "or shutdown (SIGKILL or bug in shutdown sequence)",
                    paas_resource.log_fmt()
                )
            else:
                logger.debug('%s: deployment by Git push to %r done. '
                             'git subprocess stdout/stderr: %r',
                             paas_resource.log_fmt(),
                             paas_resource.deploy_url,
                             out_err)
        paas_resource.init_cleverapps()

    @overrides
    def launch(self, paas_resource, job_data):
        paas_resource.launch(job_data)


CleverCloudHelperServiceRunner.register()


class CleverCloudFlavor:
    def __init__(self, api_data):
        """Initialize from data returned by Clever Cloud API.

        Could be from the flavor listing request, or from one of the flavors
        listed in an application

        Attributes:

        - ``api_name``: the actual names expected by Clever Cloud API
          (e.g, `'heptapod-runner-XL'`)
        - ``ram``: allocated RAM, in MiB
        - ``cpus``: number of virtual cores
        """
        # TODO actual response also includes a detailed `memory` key with
        # values such as {'unit': 'B', value: '4294967296'}
        # using it could be more robust than relying on the fact that `mem`
        # is in MiB (we'd just need to implement all decimal and binary units
        # (e.g., GB, kiB etc)
        self.api_name = api_data['name']
        self.ram_mib = api_data['mem']
        self.cpus = api_data['cpus']

    @property
    def weight(self):
        """Based on RAM footprint, with bias favoring small instances.

        The reason for the bias is that it is typically harder to fit
        large virtual machines in the available room on hypervisors. Of course
        this merely helping, not providing any kind of certainty about the
        provisionability.

        The current formula makes it so that a flavor taking 16 times the
        RAM of a smaller one counts 2 times as much as 16 of the smaller.
        """
        return (self.ram_mib / 1024) ** 1.25

    def __repr__(self):
        return "CleverCloudFlavor({'name': '%s', 'mem': %d, 'cpus': %d})" % (
            self.api_name, self.ram_mib, self.cpus
        )

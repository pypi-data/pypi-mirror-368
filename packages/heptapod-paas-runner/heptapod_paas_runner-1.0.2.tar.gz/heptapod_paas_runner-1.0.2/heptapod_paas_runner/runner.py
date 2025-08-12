# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import requests
from requests.exceptions import RequestException
import time
import toml

from .exceptions import (
    GitLabUnavailableError,
    GitLabUnexpectedError,
    JobLaunchTimeout,
    PaasResourceError,
)
from .job import JobHandle


logger = logging.getLogger(__name__)

INNER_CONFIG_EXCLUDED_ITEMS = ('heptapod_runner_main_image',
                               'paas_job_trace_watch',
                               )
"""Configuration items that are never to be forwarded to running resources.

This collection is for items that should be excluded with all concrete
subclasses of :class:`PaasRunner`.

For per-class specific rules, see :meth:`PaasRunner.is_config_item_for_inner`
"""

JOB_FAILURE_REASONS = frozenset((
    # default applied by coordinator if an unknown reason is given,
    'unknown_failure',
    'script_failure',  # ordinary job failure (no banner)
    'api_failure',
    'stuck_or_timeout_failure',
    'runner_system_failure',  # suggests in particular user to retry
    'missing_dependency_failure',
    'runner_unsupported',
    'stale_schedule',
    'job_execution_timeout',
    'archived_failure',
    'unmet_prerequisites',
    'scheduler_failure',
    'data_integrity_failure',
    'forward_deployment_failure',
    'user_blocked',
    'project_deleted',
    'ci_quota_exceeded',
    'pipeline_loop_detected',
    'trace_size_exceeded',
    'builds_disabled',
    'environment_creation_failure',
    'deployment_rejected',
    'protected_environment_failure',
    'insufficient_bridge_permissions',
    'downstream_bridge_project_not_found',
    'invalid_bridge_trigger',
    'upstream_bridge_project_not_found',
    'insufficient_upstream_permissions',
    'downstream_pipeline_creation_failed',
    'secrets_provider_not_found',
    'reached_max_descendant_pipelines_depth',
    'ip_restriction_failure',
))
"""Subset of Rails' ::Enums::Ci::CommitStatus."""


class PaasRunner:
    """Abstract base class for one of the `[[runners]]` of the main config.

    Concrete subclasses will be able to provision PAAS resources and
    launch the main Heptapod Runner's command to run one job on them.
    """

    executor = None
    """Executor name for the PAAS runner.

    Must be unique and not one of the executors provided by the main Heptapod
    Runner executable.
    """

    min_requestable_weight = 1
    """Minimum weight of job that can actually be requested from coordinator.

    If this runner is able to request the coordinator with weight limit,
    this is the weight of the smallest PAAS resource that is
    currently defined. It tells nothing about actual availability.

    On the other hand, if this runner is not able to issue requests to
    its coordinator with constraints on job weights, this must be the
    maximum weidht of all PAAS resources.

    Default value is adapted to Runners that don't have weighting
    capabilities, and excpected to be overridden by subclasses (attrivute
    or property).
    """

    @classmethod
    def register(cls):
        runner_classes[cls.executor] = cls

    @staticmethod
    def create(config):
        """Instantiate with the appropriate class."""
        return runner_classes[config['executor']](config)

    def __init__(self, config):
        self.config = config
        self.gitlab_token = self.config['token']
        # GitLab itself uses the 8 first chars in the token as a unique
        # string identifier.
        self.gitlab_api_url = self.config['url'].rstrip('/') + '/api/v4'
        self.unique_name = self.gitlab_token[:8]
        # JobHandle instances of resources kept in standby for reuse
        # TODO this will need to be serialized
        self.standby_job_handles = []

    def __repr__(self):
        return f'{self.__class__.__name__}[{self.unique_name}]'

    def discard_standby_job_handle(self, job_handle):
        """Remove job_handle from standbys if present."""
        try:
            self.standby_job_handles.remove(job_handle)
        except ValueError:
            pass

    def inner_executor(self):
        """Return executor for actual use on provisoned PAAS resource.

        To be provided by concrete classes, and must be one of the executors
        provided by the main Heptapod Runner executable.

        This is a method because a given class can use several different
        executors.
        """
        raise NotImplementedError  # pragma no cover

    def is_config_item_for_inner(self, key):
        """Tell if the given item  is to be forwarded to the PAAS resource.

        For instance, configuration items allowing to provision PAAS resources
        should not be made available to a provisioned one, so that an attack
        from a job on the runner on the PAAS resource would not leak means
        to provision infinite resources.

        This method cannot be used to allow items that are in
        :const:`INNER_CONFIG_EXCLUDED_ITEMS`.

        To be extended by concrete classes
        """
        raise NotImplementedError  # pragma no cover

    def inner_config(self):
        """Make a full configuration for use on provisioned PAAS resource.

        The produced configuration has a single `[[runner]]` section, with
        the end executor meant for the present Runner.

        It will be used with the `exec-fetched-job` command of Heptapod Runner.
        """
        # TODO should be computed and serialized (to string) only once
        inner_runner = {k: v for k, v in self.config.items()
                        if k not in INNER_CONFIG_EXCLUDED_ITEMS
                        and self.is_config_item_for_inner(k)}
        inner_runner['executor'] = self.inner_executor()
        return dict(runners=[inner_runner])

    def dump_inner_config(self, path):
        with open(path, 'w') as fobj:
            toml.dump(self.inner_config(), fobj)

    def request_job(self, max_weight=None):
        """Request one job from the coordinator

        :param max_weight: if the coordinator implements it, limit the
           weight of the requested job.
        :return: Job definition (JSON `str`) or `None` if there isn't any.
        """
        url = self.gitlab_api_url + '/jobs/request'
        post_data = dict(token=self.config['token'],
                         info=dict(executor=self.inner_executor(),
                                   features=dict(
                                       # always true (shells/abstract.go)
                                       upload_multiple_artifacts=True,
                                       upload_raw_artifacts=True,
                                       refspecs=True,
                                       artifacts=True,
                                       artifacts_exclude=True,
                                       multi_build_steps=True,
                                       return_exit_code=True,
                                       raw_variables=True,
                                       cache=True,
                                       masking=True,
                                       # true for Docker executor
                                       variables=True,
                                       image=True,
                                       services=True,
                                       session=True,
                                       terminal=True,
                                       # shared seems to be set to True
                                       # for shell, ssh and custom only.
                                       shared=False,
                                       # proxy seems to be set to True
                                       # for kubernetes only.
                                       # TODO evaluate if we shouldn't set
                                       # it for PAAS Runner
                                       proxy=False,
                                       ),
                                   )
                         )
        try:
            resp = requests.post(url, json=post_data)
        except RequestException as exc:
            raise GitLabUnavailableError(url=url, message=str(exc))

        if resp.status_code in (502, 503):
            # to be catched in main loop
            # (don't want to end everything if coordinator is temporarily
            # not available)
            raise GitLabUnavailableError(status_code=resp.status_code,
                                         message=resp.text,
                                         url=url)
        elif resp.status_code == 409:  # conflict
            # let's simply try later, same as a regular empty response
            logger.info("Got a 409 (Conflict) HTTP response from coordinator "
                        "while requesting a job from %s. Treating as no job",
                        url)
            return None
        elif resp.status_code >= 400:
            raise GitLabUnexpectedError(status_code=resp.status_code,
                                        params=None,
                                        message=resp.text,
                                        url=url)

        if resp.status_code == 204:  # no job
            return None
        return resp.text

    def is_job_finished(self, job_handle):
        # Using the API endpoint to get a job by its token
        url = self.gitlab_api_url + '/job'
        try:
            resp = requests.get(url, params=dict(job_token=job_handle.token))
        except RequestException as exc:
            raise GitLabUnavailableError(url=url, message=str(exc))
            # TODO raise the usual exceptions, just catch and log from
            # the polling method

        if resp.status_code == 401:
            # of course this is ugly, but assuming we are correct
            # on our call (proper token, on a job that was properly
            # acquired), then geting a 401 means that the job is not
            # running anymore. Doing something more natural may require
            # changes in the Rails app (or next main iteration of the Paas
            # Runner, with a proper HTTP service)
            return True
        elif resp.status_code >= 400:
            raise GitLabUnexpectedError(status_code=resp.status_code,
                                        params=None,
                                        message=resp.text,
                                        url=url)

        # TODO cancel provisioned resource if job is canceled
        status = resp.json().get('status')
        logger.debug("%s status is %r", job_handle, status)
        return status in ('failed', 'success', 'canceled')

    def gitlab_custom_attributes(self, resource_path, keys,
                                 token=None,
                                 resource_type='groups'):
        """Retrieve custom attributes with the given keys.

        :param token: if specified, is used instead of the usual runner token
        :returns: a `dict` with the wished keys. It is *not* guaranteed that
                  all are present.
        """
        if token is None:
            token = self.gitlab_token
        # if there are more than one keys, it is expected to be much
        # more efficient to list all attributes rather than issue as
        # many requests. This can be tweaked later if needed.
        url = '/'.join((self.gitlab_api_url,
                        resource_type,
                        resource_path.replace('/', '%2F'),
                        'custom_attributes'))
        resp = requests.get(url, headers={'Private-Token': token})
        if resp.status_code >= 400:
            raise GitLabUnexpectedError(status_code=resp.status_code,
                                        params=None,
                                        message=resp.text,
                                        url=url)
        return {attr['key']: attr['value'] for attr in resp.json()
                if attr['key'] in keys}

    def job_url(self, job_handle):
        return self.gitlab_api_url + '/jobs/%d' % job_handle.job_id

    def is_job_not_running(self, response):
        """Tell if the given API response is about a dead job."""
        return (response.status_code == 403
                and "Job is not running" in response.json().get('message', ''))

    def report_coordinator_job_failed(self, job_handle, reason):
        """Report job failure to coordinator

        :param str reason: should be one of :data:`JOB_FAILURE_REASONS`.
          If not, it will be converted by the coordinator to `unknown_failure`.
        """
        url = self.job_url(job_handle)
        if reason not in JOB_FAILURE_REASONS:
            logger.warning("Reporting job failure to coordinator with "
                           "unregistered reason %r behaves as if it were "
                           "'unknown_failure'", reason)
        params = dict(token=job_handle.token,
                      failure_reason=reason,
                      exit_code=103,
                      state='failed')
        resp = requests.put(url, json=params)

        if self.is_job_not_running(resp):
            logger.info("Reporting %s was not necessary, as it is already "
                        "seen as not running by the coordinator", job_handle)
        elif resp.status_code >= 400:
            params['token'] = 'REDACTED'
            raise GitLabUnexpectedError(status_code=resp.status_code,
                                        params=params,
                                        message=resp.text,
                                        url=url)

    def gl_job_send_trace(self, job_handle, message, content_range):
        """Inner method actually calling the coordinator.

        Separated to ease unit testing.
        """
        trace_url = self.job_url(job_handle) + '/trace'
        headers = {'content-range': content_range}
        resp = requests.patch(trace_url,
                              params=dict(token=job_handle.token),
                              headers=headers,
                              data=message
                              )
        if self.is_job_not_running(resp):
            logger.warning("Could not append trace to %s, as it is "
                           "seen as not running by the coordinator",
                           job_handle)
            return
        elif resp.status_code >= 400:
            raise GitLabUnexpectedError(status_code=resp.status_code,
                                        params=None,
                                        headers=headers,
                                        message=resp.text,
                                        url=trace_url)
        # resp.json() is an obscure integer code (seems to always be equal
        # to 3), not the new length.
        return resp.headers['Range']

    def job_append_trace(self, job_handle, message):
        """Append a message to the job trace (user-visible job log).

        :param message: the raw message, including any newline character.
        """
        length = len(message)
        new_trace_length = job_handle.trace_offset + length
        # given the checks that the coordinator performs, the returned
        # range from coordinator should be equal to ``0-{new_trace_length}``,
        # yet that is coincidental and one could imagine a later version
        # doing something else that changes the actual trace size
        # (unicode normalization or whatever), so better use what the
        # coordinator sent us.
        new_range = self.gl_job_send_trace(
            job_handle, message,
            f'{job_handle.trace_offset}-{new_trace_length}'
        )
        if new_range is not None:
            job_handle.trace_offset = int(new_range.split('-')[-1].strip())

    def job_wait_trace(self, project_id, job_handle, interruptible_sleep):
        """Wait for the job trace to have been updated outside this process.

        Can be used to check for full job startup, as typically the other
        system that would write to the job trace would be the inner runner
        on a provisioned resource.

        For now it depends on having a token able to read job traces.
        See #heptapod-runner42 for (better) future plans.

        :param interruptible_sleep: callable to sleep between calls, must
           return ``True`` if an interruption occurred (typically for
           general shutdown).
        :returns: ``True`` if a trace not written by this process
            has been detected, ``False`` if sleep between polling requests
            was interrupted.
        :raises: PaasResourceError in case of timeout
        """
        watch_conf = self.config.get('paas_job_trace_watch', {})
        token = watch_conf.get('token')
        if token is None:
            logger.warning("Missing token for job trace watching, will have "
                           "to assume it to be ok.")
            return True

        timeout = watch_conf.get('timeout_seconds', 300)
        poll_step = watch_conf.get('poll_step', 10)
        job_id = job_handle.job_id

        start = time.time()
        while time.time() - start < timeout:
            trace = self.gl_job_get_trace(project_id, job_id, token)
            if len(trace) > job_handle.trace_offset:
                logger.info("%s is fully launched (job trace update detected)",
                            job_handle)
                return True
            if interruptible_sleep(poll_step):
                return False

        raise JobLaunchTimeout(job_handle, timeout)

    def gl_job_get_trace(self, project_id, job_id, token):
        """Get the job trace for given handle, using the given token.

        In case of server side error (including 503), return an empty string.
        Because this is typically used in a polling loop, such swallowing
        is actually retrying.

        In case of 404 (Not Found) or 429 (Too Many Requests),
        an empty string is also returned for the same reasons. Note:
        according to https://docs.gitlab.com/ce/api/jobs.html#get-a-log-file,
        a 404 can be returned if there's no trace.

        :raises: :class:`GitLabUnexpectedError` in case of other client-side
          errors, as they are not supposed to happen (bad token)
        """
        trace_url = (self.gitlab_api_url
                     + f'/projects/{project_id}/jobs/{job_id}/trace')

        resp = requests.get(trace_url, headers={'Private-Token': token})

        code = resp.status_code
        if code < 400:
            return resp.text

        if code in (429, 404) or code >= 500:
            return ''

        raise GitLabUnexpectedError(url=trace_url,
                                    status_code=code,
                                    params=None,
                                    message=resp.text)

    def standby_weight(self):
        """Return the weight of all standing by PAAS resources."""
        return sum(jh.paas_resource.weight
                   for jh in self.standby_job_handles)

    def provision(self, job):
        """Provision necessary resources in which to actually run the job.

        To be implemented by subclasses
        """
        raise NotImplementedError('provision')  # pragma no cover

    def expected_weight(self, job):
        """Return the weight of the job without launching it.

        This is just an expected weight because it is possible (yet very
        uncommon) that the PAAS definitions change between this call
        and the actual provisioning.

        Default value is adapted to Runners that don't have weighting
        capabilities.
        """
        return 1

    def launch(self, paas_resource, job_data):
        """Schedule the job to run on the given PAAS resource.

        To be implemented by subclasses
        """
        raise NotImplementedError('launch')  # pragma no cover

    def decommission(self, paas_resource):
        """Delete the PAAS resource.

        Should not raise an error if the resource was already absent.

        :return: ``True`` if it was actually deleted, and ``False`` otherwise.
        """
        raise NotImplementedError('decommission')  # pragma no cover

    def load_paas_resource(self, data):
        """Create a full PAAS resource from minimal extracted data.

        Given a resource ``rsc`` created by this Runner instance,
        ``self.load_paas_resouce(rsc.dump())`` should give back a
        fully functional new resource.

        Typically will be used for state save before shutdown and restoration
        after startup, perhaps using changed configuration accessible from
        the Runner.
        """
        raise NotImplementedError("load_paas_resource")  # pragma no cover

    def pop_standby_for_weight(self, weight):
        """Return a standby job handle for the given weight and remove it.

        :returns: ``None`` if no standby available for the give weight.
        """
        standby = self.standby_job_handles

        # TODO filter by checking tenant
        # Reusing the oldest possible, so increase chances of caches
        # being warm (and of disks to be full, sadly)
        for i, old_jh in enumerate(standby):
            # Avoid using too large a resource, as this is wasteful in the
            # absolute, and it might be needed soon afterwards.
            # TODO make this configurable
            ratio = old_jh.paas_resource.weight / weight
            if ratio >= 1 and ratio < 1.15:
                break
        else:
            return None

        del standby[i]
        return old_jh

    def launch_reuse_resource(self, job_data, weight, old_jh):
        """Launch a job by using a standby resource.

        :return: the job handle the standby resource was previously
          attached to and a new job handle

        Actual implementation to be provided by subclasses with
        reuse capabilities
        """
        new_jh = JobHandle(job_id=job_data['id'],
                           runner_name=self.unique_name,
                           expected_weight=weight,
                           token=job_data['token'])
        rsc = new_jh.paas_resource = old_jh.paas_resource
        try:
            rsc.launch(job_data)
        except PaasResourceError as exc:
            logger.warning(
                "Should have been able to reuse resource of %s to run %s,"
                "but it failed as %s.", old_jh, new_jh, exc)
            return None

        return new_jh

    def choose_resources_for_decommission(self, weight):
        """Chooses standby resources to decommission for the given weight.

        The resources are returned as their original :class:`JobHandle`
        and immediately forgotten by the runner. The runner does not
        take care of the decommission itself, the caller will have to
        do them (typically in separate threads).
        """
        standby = self.standby_job_handles
        if not standby:
            return ()

        to_decom = []
        to_decom_weight = 0

        # We will eventually want something smarter, perhaps taking
        # tenant into account.
        for i, jh in enumerate(standby):
            to_decom.append(jh)
            to_decom_weight += jh.paas_resource.weight
            if to_decom_weight >= weight:
                break

        self.standby_job_handles = standby[i+1:]
        return to_decom


runner_classes = {}
"""Mapping of executor to runner class."""

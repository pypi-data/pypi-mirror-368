# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later
from io import StringIO
import re

from .grpc.heptapod_paas_runner_pb2 import Job as GRPCJob


class JobHandle:
    """Represent a job provided by a coordinator.

    - :attr:`job_id` the numeric id, relative to the coordinator
    - :attr:`runner_name` the unique name of the Runner instance that
      was used to acquire the job
    - :attr:`token` authentication token to the coordinator.

    This class is meant to be message passing payload, hence does not
    have heavy attributes.

    With the Runner instance (usually can be retrieved from its unique name)
    and :attr:`token`, all jobs details can be retrieved from coordinator.
    Some of them (status, notably) can change over time.
    We could therefore use ``(runner_name, token)`` as a full ID, but
    :attr:`token` must stay secret and never be leaked to the logs, which
    could otherwise happen easily on changes of this class.
    """

    paas_resource = None
    """Attribute to keep track of provisioned resource, if any."""

    def __init__(self, runner_name, job_id, token,
                 trace_offset=0,
                 expected_weight=1):
        self.runner_name = runner_name
        self.job_id = job_id
        self.token = token
        self.full_id = (runner_name, job_id)
        self.expected_weight = expected_weight
        self.trace_offset = trace_offset

    @classmethod
    def load(cls, runner, data):
        rsc_data = data.pop('paas_resource', None)
        handle = cls(**data)
        if rsc_data is not None:
            handle.paas_resource = runner.load_paas_resource(rsc_data)
        return handle

    def as_grpc(self):
        return GRPCJob(job_id=self.job_id,
                       runner_name=self.runner_name)

    def weight_correction(self):
        return self.paas_resource.weight - self.expected_weight

    def actual_or_expected_weight(self):
        if self.paas_resource is not None:
            return self.paas_resource.weight
        return self.expected_weight

    def finished_standby_seconds(self):
        """Time to keep the resource standing by after job is finished.

        This allows reuse.

        We could later on use negative numbers to indicate that the
        resource is kept permanently warm (like Docker Machine executor
        does),
        """
        rsc = self.paas_resource
        return 0 if rsc is None else rsc.finished_standby_seconds()

    def dump(self):
        res = {attr: getattr(self, attr)
               for attr in ('runner_name',
                            'job_id',
                            'token',
                            'trace_offset',
                            'expected_weight')}
        if self.paas_resource is not None:
            res['paas_resource'] = self.paas_resource.dump()
        return res

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.full_id == other.full_id)

    def __hash__(self):
        return hash(self.full_id)

    def __repr__(self):
        return 'JobHandle(runner_name=%r, job_id=%d, token="REDACTED")' % (
            self.runner_name, self.job_id)

    def __str__(self):
        return 'job %d for runner %r' % (self.job_id, self.runner_name)

    def log_fmt(self):
        """Alternative to str() and repr() useful to log pending jobs."""
        rsc = self.paas_resource
        rsc_log = None if rsc is None else rsc.log_fmt()
        return (f'JobHandle<id={self.job_id}, runner={self.runner_name!r}, '
                f'resource={rsc_log}>')


def jobs_log_fmt(collection):
    """Format for logs a collection of jobs.

    :param collectio: any iterable of job handles. Notably formats the
      *keys* of :class:`dict`s such as ``PaasDispatcher.pending_jobs``.
    """
    stream = StringIO()
    stream.write('[')
    first = True
    for handle in collection:
        if not first:
            stream.write(', ')
        stream.write(handle.log_fmt())
        first = False
    stream.write(']')
    return stream.getvalue()


def get_job_variable(job_data, name):
    """Extract the variable with given name from job data dict.

    :returns: the variable value as string or ``None`` if it doesn't exist.
    """
    for var in job_data.get('variables', ()):
        if var['key'] == name:
            return var['value']


def all_job_variables(job_data):
    """Return a `dict for all variables in job_data.

    All values stay simple strings.
    """
    return {v['key']: v['value'] for v in job_data.get('variables', ())}


VAR_SUBST_RX = re.compile(r'\$([a-zA-Z0-9_]+|{.+?})')
r"""Regular expression for variables substitution

Implementation notes:

- not using `\w` to avoid a doc lookup for people wondering about edge cases
  (underscore, dash) and to avoid the need for `re.ASCII` option. See also
  https://docs.python.org/3/howto/regex.html#matching-characters
"""


def expand_variables(s, job_vars):
    """Expand given string with the given job variables.

    This is meant to be the same as GitLab Runner would do, with
    substitution syntax being either:

    - ``$`` followed by alphanumerics (stop at first non-alphanum)
    - or ``${`` up to the first ``}`` (ignoring nesting, clearly)

    (this is what Gos' ``os.ExpandVar`` does

    See heptapod-runner#25 for more details.

    Pretty much everything is understood with the braces notation::

      >>> expand_variables('somethin-${FOO-BAR}-hop', {'FOO-BAR': "foo"})
      'somethin-foo-hop'
      >>> expand_variables('somethin-${FOO-BAR}-hop', {'FOO-BAR': "foo"})
      'somethin-foo-hop'
      >>> expand_variables('somethin-${F#*$&}-hop', {'F#*$&': "foo"})
      'somethin-foo-hop'

    Without braces, variable names in pattern are restricted to
    alphanumeric ASCII chars and underscores::

      >>> expand_variables('somethin-$FOO_BAR-hop', {'FOO_BAR': "foo"})
      'somethin-foo-hop'
      >>> expand_variables('$FOO_BAR-hop', dict(FOO_BAR="foo"))
      'foo-hop'
      >>> expand_variables('somethin-$FOO-BAR-hop', {'FOO-BAR': "foo"})
      'somethin--BAR-hop'

    Special cases for uniformity with Golang implementation (checked with
    the online playfield at https://pkg.go.dev/os#Expand)::

      >>> expand_variables('somethin-${FOO-${BAR}}-hop', {'FOO-BAR': "foo"})
      'somethin-}-hop'
      >>> expand_variables('somethin-${FOO-${BAR}}-hop', {'FOO-${BAR': "foo"})
      'somethin-foo}-hop'

    Logically nested (but not syntactically)::

      >>> expand_variables('somethin-${FOO}-hop',
      ...                  {'FOO': "foo${BAR}", 'BAR': "bar"})
      'somethin-foobar-hop'
    """
    def repl(match):
        # perhaps a more clever regexp would prevent the need to strip braces
        return expand_variables(job_vars.get(match.group(1).strip('{}'), ''),
                                job_vars)

    return VAR_SUBST_RX.sub(repl, s)

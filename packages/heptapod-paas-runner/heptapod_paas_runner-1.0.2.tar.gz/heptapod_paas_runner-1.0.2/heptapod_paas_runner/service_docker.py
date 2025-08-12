import logging
from overrides import overrides

from .runner import PaasRunner
from .paas_resource import PaasHelperServiceResource

from .testing import FlavorForTests

logger = logging.getLogger(__name__)


class ServiceDockerRunner(PaasRunner):
    """Using a fixed instance of the Heptapod PAAS Runner Helper service.

    The service being meant to be run in provisioned resources, this is,
    like `LocalDocker` a simple testbed.
    """

    executor = 'service-docker'
    available_flavors = {'M': FlavorForTests(1)}

    def __init__(self, config):
        super(ServiceDockerRunner, self).__init__(config)

        self.host = self.config.get('paas-runner-helper-host',
                                    'localhost:8000')
        self.http1 = self.config.get('paas-runner-helper-http1', False)
        self.paas_token = self.config.get('paas-runner-helper-token')

    @overrides
    def inner_executor(self):
        return 'docker'

    @overrides
    def is_config_item_for_inner(self, key):
        """All config parameters except `host` are standard.

        `host`, the Docker endpoint URL is meaningful for the dispatcher only,
        and is mounted at a fixed place for the inner executor.
        """
        return not key.startswith('paas-runner-helper-')

    @overrides
    def provision(self, job):
        app_id = 'hpd-job-%s' % self.unique_name.lower()
        return ServiceApplication(self, app_id, self.host,
                                  http1=self.http1,
                                  paas_token=self.paas_token)

    @overrides
    def load_paas_resource(self, data):
        data['http1'] = self.http1
        return ServiceApplication(self, **data)

    @overrides
    def launch(self, paas_resource, job_data):
        return paas_resource.launch(job_data)

    @overrides
    def is_job_finished(self, job_handle):
        resource = job_handle.paas_resource
        if resource is None:
            logger.warning(
                "Tracking state of %s, but lacks PAAS Resource descriptor. "
                "Considered finished by default", job_handle)
            return True
        return resource.is_finished(job_handle)

    @overrides
    def decommission(self, paas_resource):
        if paas_resource.grpc:
            paas_resource.channel.close()


ServiceDockerRunner.register()


class ServiceApplication(PaasHelperServiceResource):
    weight = 1
    service_tls = False
    # very short delay and timeout to avoid slowing down unit tests
    can_take_job_delay = 0.001
    can_take_job_timeout = 0.05

    def __init__(self, runner, app_id, netloc, http1, paas_token=None):
        self.paas_token = paas_token
        self.init_paas_token()
        init = self.init_http1 if http1 else self.init_grpc
        init(runner, app_id, netloc)

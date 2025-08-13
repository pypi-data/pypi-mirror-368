from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRequestsConftestBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_conftest"
    template = "requests-conftest"

    def _get_output_module(self):
        return "tests.requests.conftest"

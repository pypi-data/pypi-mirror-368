from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRequestsTestRequestsBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_tests"
    template = "requests-tests"

    def _get_output_module(self):
        return "tests.requests.test_requests"

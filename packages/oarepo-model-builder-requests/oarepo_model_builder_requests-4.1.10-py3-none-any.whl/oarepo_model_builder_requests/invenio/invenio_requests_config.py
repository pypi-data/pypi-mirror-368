from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRequestsConfigBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_config"
    section = "config"
    template = "requests-config"

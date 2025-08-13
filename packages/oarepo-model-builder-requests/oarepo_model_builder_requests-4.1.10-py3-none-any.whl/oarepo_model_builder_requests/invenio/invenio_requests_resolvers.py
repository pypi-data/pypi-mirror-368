from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRequestsResolversBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_resolvers"
    section = "record-resolver"
    template = "requests-resolvers"

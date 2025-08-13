from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRequestsViewsBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_views"
    template = "requests-views"
    section = "api-blueprint"

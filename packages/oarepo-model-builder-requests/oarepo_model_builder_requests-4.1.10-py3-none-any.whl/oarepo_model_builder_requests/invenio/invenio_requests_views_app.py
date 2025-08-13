from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRequestsViewsAppBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_views_app"
    template = "requests-views"
    section = "app-blueprint"

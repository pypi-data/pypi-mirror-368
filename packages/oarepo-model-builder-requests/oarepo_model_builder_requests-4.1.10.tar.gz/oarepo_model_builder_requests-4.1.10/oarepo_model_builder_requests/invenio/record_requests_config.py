from oarepo_model_builder_requests.invenio.overriding_builder import OverridingBuilder


class RecordRequestsConfigBuilder(OverridingBuilder):
    TYPE = "record_requests_requests_config"
    section = "config"
    template = "config"
    overriden_sections = {
        "resource": "record-requests.resource",
        "service": "record-requests.service",
    }

from oarepo_model_builder_requests.invenio.overriding_builder import OverridingBuilder


class RecordRequestTypesConfigBuilder(OverridingBuilder):
    TYPE = "record_request_types_requests_config"
    section = "config"
    template = "config"
    overriden_sections = {
        "resource": "record-request-types.resource",
        "service": "record-request-types.service",
    }

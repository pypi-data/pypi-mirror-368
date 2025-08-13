from oarepo_model_builder_requests.invenio.overriding_builder import OverridingBuilder


class RecordRequestTypesExtResourceBuilder(OverridingBuilder):
    TYPE = "record_request_types_ext_resource"
    section = "ext"
    template = "requests-ext-resource"
    overriden_sections = {
        "resource": "record-request-types.resource",
        "service": "record-request-types.service",
    }

    def finish(self, **extra_kwargs):
        ext = self.current_model.section_record_request_types_ext_resource.config
        super().finish(ext=ext, **extra_kwargs)

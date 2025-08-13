from oarepo_model_builder_requests.invenio.overriding_builder import OverridingBuilder


class RecordRequestTypesAPIViewsBuilder(OverridingBuilder):
    TYPE = "record_request_types_api_views"
    section = "record-request-types.api-blueprint"
    template = "api-views"
    overriden_sections = {"api-blueprint": "record-request-types.api-blueprint"}

    def finish(self, **extra_kwargs):
        ext = self.current_model.section_record_request_types_ext_resource.config
        super().finish(ext=ext, **extra_kwargs)

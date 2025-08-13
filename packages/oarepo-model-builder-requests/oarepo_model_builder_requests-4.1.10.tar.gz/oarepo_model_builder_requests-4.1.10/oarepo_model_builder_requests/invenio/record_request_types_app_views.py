from oarepo_model_builder_requests.invenio.overriding_builder import OverridingBuilder


class RecordRequestTypesAPPViewsBuilder(OverridingBuilder):
    TYPE = "record_request_types_app_views"
    section = "record-request-types.app-blueprint"
    template = "app-views"
    overriden_sections = {"app-blueprint": "record-request-types.app-blueprint"}

    def finish(self, **extra_kwargs):
        ext = self.current_model.section_record_request_types_ext_resource.config
        super().finish(ext=ext, **extra_kwargs)

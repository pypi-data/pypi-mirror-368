from oarepo_model_builder_requests.invenio.overriding_builder import OverridingBuilder


class RecordRequestsAPIViewsBuilder(OverridingBuilder):
    TYPE = "record_requests_api_views"
    section = "record-requests.api-blueprint"
    template = "api-views"
    overriden_sections = {"api-blueprint": "record-requests.api-blueprint"}

    def finish(self, **extra_kwargs):
        ext = self.current_model.section_record_requests_ext_resource.config
        super().finish(ext=ext, **extra_kwargs)

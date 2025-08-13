from oarepo_model_builder_requests.invenio.overriding_builder import OverridingBuilder


class RecordRequestsAPPViewsBuilder(OverridingBuilder):
    TYPE = "record_requests_app_views"
    section = "record-requests.app-blueprint"
    template = "app-views"
    overriden_sections = {"app-blueprint": "record-requests.app-blueprint"}

    def finish(self, **extra_kwargs):
        ext = self.current_model.section_record_requests_ext_resource.config
        super().finish(ext=ext, **extra_kwargs)

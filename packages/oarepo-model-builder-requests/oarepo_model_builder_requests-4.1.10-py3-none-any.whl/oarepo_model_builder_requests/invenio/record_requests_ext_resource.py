from oarepo_model_builder_requests.invenio.overriding_builder import OverridingBuilder


class RecordRequestsExtResourceBuilder(OverridingBuilder):
    TYPE = "record_requests_ext_resource"
    section = "ext"
    template = "requests-ext-resource"
    overriden_sections = {
        "resource": "record-requests.resource",
        "service": "record-requests.service",
    }

    def finish(self, **extra_kwargs):
        ext = self.current_model.section_record_requests_ext_resource.config
        super().finish(ext=ext, **extra_kwargs)

from oarepo_model_builder.datatypes.datatypes import MergedAttrDict
from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder
from oarepo_model_builder.utils.dict import dict_get


class OverridingBuilder(InvenioBaseClassPythonBuilder):
    overriden_sections = {}

    @property
    def generate(self):
        if hasattr(self, "section") and dict_get(
            self.current_model.definition, [*self.section.split("."), "skip"], False
        ):
            return False

        if (
            self.skip_if_not_generating
            and hasattr(self, "section")
            and not dict_get(
                self.current_model.definition,
                [*self.section.split("."), "generate"],
                False,
            )
        ):
            return False
        return True

    def _get_output_module(self):
        module = dict_get(
            self.current_model.definition, [*self.section.split("."), "module"]
        )
        return module

    @property
    def vars(self):
        vars = super().vars
        overrides = {}
        for overriden_section, source_section in self.overriden_sections.items():
            overriden_data = dict_get(vars, source_section.split("."), {})
            overrides[overriden_section] = overriden_data
        return MergedAttrDict(overrides, vars)

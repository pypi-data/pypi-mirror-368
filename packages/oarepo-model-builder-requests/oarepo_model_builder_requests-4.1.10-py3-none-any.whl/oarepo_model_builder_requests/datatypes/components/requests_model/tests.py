from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder_tests.datatypes.components import ModelTestComponent


class RequestsTestComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [ModelTestComponent]

    def process_tests(self, datatype, section, **extra_kwargs):
        section.constants["skip_search_test"] = True

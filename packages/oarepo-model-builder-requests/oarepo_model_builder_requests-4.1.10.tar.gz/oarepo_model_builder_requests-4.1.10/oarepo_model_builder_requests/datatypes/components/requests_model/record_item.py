from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import RecordItemModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default


class RequestsRecordItemModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [RecordItemModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        record_item_config = set_default(datatype, "record-item", {})
        record_item_config.setdefault("components", [])
        record_item_config["components"] += [
            "{{oarepo_requests.services.results.RequestsComponent}}()",
            "{{oarepo_requests.services.results.RequestTypesComponent}}()",
        ]

from typing import Dict

from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import UIMarshmallowModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default


class RequestsUIMarshmallowModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [UIMarshmallowModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile in {"record", "draft"}:
            marshmallow: Dict = set_default(datatype, "ui", "marshmallow", {})
            marshmallow["base-classes"].insert(
                0, "oarepo_requests.services.ui_schema.UIRequestsSerializationMixin"
            )

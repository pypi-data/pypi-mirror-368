import marshmallow as ma
from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components.model.defaults import (
    DefaultsModelComponent,
)
from oarepo_model_builder.datatypes.components.model.utils import set_default
from oarepo_model_builder.validation.utils import ImportSchema


class UIRecordResolverClassSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    generate = ma.fields.Bool()
    class_ = ma.fields.Str(
        attribute="class",
        data_key="class",
    )
    extra_code = ma.fields.Str(
        attribute="extra-code",
        data_key="extra-code",
    )
    module = ma.fields.String(metadata={"doc": "Class module"})
    imports = ma.fields.List(
        ma.fields.Nested(ImportSchema), metadata={"doc": "List of python imports"}
    )
    skip = ma.fields.Boolean()


class UIRecordResolverComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [DefaultsModelComponent]

    class ModelSchema(ma.Schema):
        ui_record_resolver = ma.fields.Nested(
            UIRecordResolverClassSchema,
            attribute="ui-record-resolver",
            data_key="ui-record-resolver",
        )

    def before_model_prepare(self, datatype, *, context, **kwargs):
        module = datatype.definition["module"]["qualified"]
        profile_module = context["profile_module"]
        profile = datatype.root.profile

        ui_record_resolver = set_default(datatype, "ui-record-resolver", {})

        if profile not in {
            "record",
            "draft",
        }:
            ui_record_resolver.setdefault("generate", False)
            ui_record_resolver.setdefault("skip", True)
            return

        ui_record_resolver.setdefault("generate", True)
        if profile == "record":
            ui_record_resolver.setdefault(
                "class",
                "oarepo_requests.resolvers.ui.RecordEntityReferenceUIResolver",
            )
        elif profile == "draft":
            ui_record_resolver.setdefault(
                "class",
                "oarepo_requests.resolvers.ui.RecordEntityDraftReferenceUIResolver",
            )

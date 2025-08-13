from oarepo_model_builder.invenio.invenio_record_resource_setup_cfg import (
    InvenioRecordResourceSetupCfgBuilder,
)
from oarepo_model_builder.outputs.cfg import CFGOutput
from oarepo_model_builder.utils.python_name import split_package_base_name


class RecordRequestsResourceSetupCfgBuilder(InvenioRecordResourceSetupCfgBuilder):
    TYPE = "record_requests_resource_setup_cfg"
    key = "record-requests"

    def finish(self):
        super().finish()
        definition = self.current_model.definition[self.key]
        output: CFGOutput = self.builder.get_output("cfg", "setup.cfg")

        register_function = split_package_base_name(
            definition["api-blueprint"]["function"]
        )

        output.add_entry_point(
            "invenio_base.api_blueprints",
            definition["api-blueprint"]["alias"],
            f"{register_function[0]}:{register_function[-1]}",
        )

        register_function = split_package_base_name(
            definition["app-blueprint"]["function"]
        )

        output.add_entry_point(
            "invenio_base.blueprints",
            definition["app-blueprint"]["alias"],
            f"{register_function[0]}:{register_function[-1]}",
        )

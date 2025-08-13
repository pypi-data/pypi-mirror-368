from oarepo_model_builder.builders import OutputBuilder
from oarepo_model_builder.outputs.cfg import CFGOutput


class RequestsSetupCfgBuilder(OutputBuilder):
    TYPE = "requests_setup_cfg"

    def finish(self):
        super().finish()

        output: CFGOutput = self.builder.get_output("cfg", "setup.cfg")

        output.add_dependency("oarepo-requests", ">=1.0.2")

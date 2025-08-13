from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRequestsBuilder(InvenioBaseClassPythonBuilder):
    """
    base for builders based on processing template for each request separately
    """

    def get_vars_or_none_if_no_requests(self):
        super(
            InvenioBaseClassPythonBuilder, self
        ).finish()  # calls super().finish() of InvenioBaseClassPythonBuilder
        vars = self.vars
        if (
            "requests" not in vars
            or not vars["requests"]
            or "types" not in vars["requests"]
        ):
            return None
        return vars

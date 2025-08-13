
from oarepo_model_builder_requests.invenio.record_requests_resource_setup_cfg import (
    RecordRequestsResourceSetupCfgBuilder,
)


class RecordRequestTypesResourceSetupCfgBuilder(RecordRequestsResourceSetupCfgBuilder):
    TYPE = "record_request_types_resource_setup_cfg"
    key = "record-request-types"

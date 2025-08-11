from vital_ai_vitalsigns.metaql.metaql_query import MetaQLQuery

from kgraphservice.rest.model.kgraphservice_kgraph_list import KGraphServiceKGraphList
from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp
from kgraphservice.rest.model.kgraphservice_query import KGraphServiceQuery
from kgraphservice.rest.model.kgraphservice_request import KGraphServiceRequest
from kgraphservice.rest.model.kgraphservice_response import KGraphServiceResponse
from kgraphservice.rest.model.kgraphservice_results import KGraphServiceResults
from kgraphservice.rest.model.kgraphservice_status import KGraphServiceStatus, OK_KGRAPHSERVICE_STATUS_TYPE


class KGraphServiceBuilder:

    @classmethod
    def build_request(cls, *,
                      account_uri: str = "",
                      account_id: str = "",
                      login_uri: str = "",
                      jwt_token: str = "",
                      request_op: KGraphServiceOp) -> KGraphServiceRequest:

        request = KGraphServiceRequest(
            kgraphservice_class="KGraphServiceRequest",
            account_uri=account_uri,
            account_id=account_id,
            login_uri=login_uri,
            jwt_token=jwt_token,
            request=request_op
        )

        return request

    @classmethod
    def build_kgraph_list_op(cls) -> KGraphServiceKGraphList:

        op = KGraphServiceKGraphList(
            kgraphservice_class="KGraphServiceKGraphList"
        )

        return op

    @classmethod
    def build_query_op(cls, *, metaql_query: MetaQLQuery) -> KGraphServiceQuery:

        op = KGraphServiceQuery(
            kgraphservice_class="KGraphServiceQuery",
            metaql_query=metaql_query
        )

        return op

    @classmethod
    def build_response(cls, *, results_dict: dict) -> dict:

        status = KGraphServiceStatus(
            kgraphservice_class='KGraphServiceStatus',
            status_type=OK_KGRAPHSERVICE_STATUS_TYPE,
            status_code=0,
            status_message=None
        )

        results = KGraphServiceResults(
            kgraphservice_class='KGraphServiceResults',
            results_dict=results_dict
        )

        response = KGraphServiceResponse(
            kgraphservice_class='KGraphServiceResponse',
            modification=None,
            status=status,
            results=results
        )

        return response


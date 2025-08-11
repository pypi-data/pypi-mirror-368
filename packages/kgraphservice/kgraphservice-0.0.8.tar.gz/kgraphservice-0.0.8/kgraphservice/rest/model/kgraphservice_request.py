from typing_extensions import TypedDict

from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp


class KGraphServiceRequest(TypedDict):

    kgraphservice_class: str

    account_uri: str

    account_id: str

    login_uri: str

    jwt_token: str

    request: KGraphServiceOp





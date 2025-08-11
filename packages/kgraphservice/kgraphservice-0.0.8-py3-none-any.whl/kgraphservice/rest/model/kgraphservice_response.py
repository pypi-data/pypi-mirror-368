from typing import Optional

from typing_extensions import TypedDict

from kgraphservice.rest.model.kgraphservice_modification import KGraphServiceModification
from kgraphservice.rest.model.kgraphservice_results import KGraphServiceResults
from kgraphservice.rest.model.kgraphservice_status import KGraphServiceStatus


class KGraphServiceResponse(TypedDict):

    kgraphservice_class: str

    status: KGraphServiceStatus

    results: Optional[KGraphServiceResults]

    modification: Optional[KGraphServiceModification]


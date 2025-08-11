from vital_ai_vitalsigns.metaql.metaql_query import MetaQLQuery

from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp


class KGraphServiceQuery(KGraphServiceOp):

    metaql_query: MetaQLQuery


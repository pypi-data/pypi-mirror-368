from vital_ai_vitalsigns.metaql.metaql_query import SelectQuery, GraphQuery
from vital_ai_vitalsigns.metaql.metaql_result_element import MetaQLResultElement
from vital_ai_vitalsigns.metaql.metaql_result_list import MetaQLResultList
from vital_ai_vitalsigns.query.metaql_result import MetaQLResult
from vital_ai_vitalsigns.service.vital_service import VitalService
from kgraphservice.rest.impl.kgraphservice_builder import KGraphServiceBuilder
from kgraphservice.rest.impl.kgraphservice_parser import KGraphServiceParser


# parser for server to parse requests
# generator for client to generate requests

# parser for client to parse responses
# generator for server to generate responses

class KGraphServiceRESTImpl:

    def __init__(self, *, vitalservice: VitalService):
        self._vitalservice = vitalservice

    def handle_request(self, request) -> dict:

        op_dict = KGraphServiceParser.parse_kgraphservice_request(request)

        kgraphservice_class = op_dict.get('kgraphservice_class')

        if kgraphservice_class is None:
            response = {'response': 'error'}
            return response

        if kgraphservice_class == 'KGraphServiceKGraphList':

            graph_list = self._vitalservice.list_graphs()

            results_dict = {
                'graph_list': graph_list
            }

            response = KGraphServiceBuilder.build_response(
                results_dict=results_dict
            )

            return response

        if kgraphservice_class == 'KGraphServiceQuery':

            metaql_query: SelectQuery | GraphQuery | None = op_dict.get('metaql_query', None)

            print(metaql_query)

            if metaql_query is not None:

                metaql_class = metaql_query.get('metaql_class', None)

                if metaql_class == 'SelectQuery':

                    select_query: SelectQuery = metaql_query

                    print(f"Select Query: {select_query}")

                    metaql_result: MetaQLResult = self._vitalservice.metaql_select_query(
                        # namespace="",
                        select_query=select_query,
                        namespace_list=[]
                    )

                    # print(f"MetaQLResult: {metaql_result}")

                    result_list = []

                    for re in metaql_result.get_result_list():
                        go = re.graph_object
                        score = re.score

                        metaql_re = MetaQLResultElement(
                            metaql_class="MetaQLResultElement",
                            graph_object=go,
                            score=score,
                        )
                        result_list.append(metaql_re)

                    metaql_result_list = MetaQLResultList(
                        metaql_class="MetaQLResultList",
                        offset=metaql_result.get_offset(),
                        limit=metaql_result.get_limit(),
                        result_count=metaql_result.get_result_count(),
                        total_result_count=metaql_result.get_total_result_count(),
                        binding_list=[],
                        result_list=result_list,
                        result_object_list=[]
                    )

                    results_dict = metaql_result_list

                    response = KGraphServiceBuilder.build_response(
                        results_dict=results_dict
                    )

                    return response

                if metaql_class == 'GraphQuery':

                    graph_query: GraphQuery = metaql_query

                    print(f"Graph Query: {graph_query}")

                    metaql_result: MetaQLResult = self._vitalservice.metaql_graph_query(
                        graph_query=graph_query
                    )

                    # print(f"MetaQLResult: {metaql_result}")

                    result_list = []

                    for re in metaql_result.get_result_list():
                        go = re.graph_object
                        score = re.score

                        metaql_re = MetaQLResultElement(
                            metaql_class="MetaQLResultElement",
                            graph_object=go,
                            score=score,
                        )
                        result_list.append(metaql_re)

                    metaql_result_list = MetaQLResultList(
                        metaql_class="MetaQLResultList",
                        offset=metaql_result.get_offset(),
                        limit=metaql_result.get_limit(),
                        result_count=metaql_result.get_result_count(),
                        total_result_count=metaql_result.get_total_result_count(),
                        binding_list=metaql_result.get_binding_list(),
                        result_list=result_list,
                        result_object_list=metaql_result.get_result_object_list()
                    )

                    results_dict = metaql_result_list

                    response = KGraphServiceBuilder.build_response(
                        results_dict=results_dict
                    )

                    return response

        response = {'response': 'unknown'}

        return response

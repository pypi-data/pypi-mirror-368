import json

from kgraphservice.rest.model.kgraphservice_kgraph_list import KGraphServiceKGraphList
from kgraphservice.rest.model.kgraphservice_query import KGraphServiceQuery
from kgraphservice.rest.model.kgraphservice_results import KGraphServiceResults


class KGraphServiceParser:

    @classmethod
    def parse_kgraphservice_request(cls, kgraphservice_request_dict: dict) -> dict | None:

        kgraphservice_class = kgraphservice_request_dict.get("kgraphservice_class", None)

        if kgraphservice_class == 'KGraphServiceRequest':

            account_uri = kgraphservice_request_dict.get("account_uri", None)
            account_id = kgraphservice_request_dict.get("account_id", None)
            login_uri = kgraphservice_request_dict.get("login_uri", None)
            jwt_token = kgraphservice_request_dict.get("jwt_token", None)

            request = kgraphservice_request_dict.get("request", None)

            if request:
                return cls.parse_kgraphservice_class(request)

        return None

    @classmethod
    def parse_kgraphservice_response(cls, kgraphservice_response_dict: dict) -> dict | None:

        # print(kgraphservice_response_dict)

        kgraphservice_class = kgraphservice_response_dict.get("kgraphservice_class", None)

        if kgraphservice_class == 'KGraphServiceResponse':

            results: dict | None = kgraphservice_response_dict.get("results", None)

            if results is not None:
                results_dict = cls.parse_kgraphservice_class(results)
                # print(results_dict)
                return results_dict

        return None

    @classmethod
    def parse_kgraphservice_class(cls, kgservice_dict: dict) -> dict | None:

        kgraphservice_class = kgservice_dict.get("kgraphservice_class", None)

        if kgraphservice_class is None:
            return None

        parse_dict = dict()

        for k, v in kgservice_dict.items():

            if isinstance(v, dict):

                v_kgraphservice_class = v.get("kgraphservice_class", None)

                # pass through non kgraphservice maps
                if v_kgraphservice_class is None:
                    parse_dict[k] = v
                else:
                    # parse the kgraphservice maps
                    v_dict = cls.parse_kgraphservice_class(v)
                    parse_dict[k] = v_dict

            elif isinstance(v, list):
                parse_list = []
                for e in v:
                    if isinstance(e, dict):
                        e_dict = cls.parse_kgraphservice_class(e)
                        parse_list.append(e_dict)
                    else:
                        parse_list.append(e)
                parse_dict[k] = parse_list

            else:
                if k != 'kgraphservice_class':
                    parse_dict[k] = v

        if kgraphservice_class == 'KGraphServiceKGraphList':

            op_dict = KGraphServiceKGraphList(
                kgraphservice_class='KGraphServiceKGraphList',
            )

            return op_dict

        if kgraphservice_class == 'KGraphServiceQuery':

            # potentially use MetaQLParser
            metaql_query = parse_dict['metaql_query']

            op_dict = KGraphServiceQuery(
                kgraphservice_class='KGraphServiceQuery',
                metaql_query=metaql_query
            )

            return op_dict

        if kgraphservice_class == 'KGraphServiceResults':

            results = KGraphServiceResults(
                kgraphservice_class='KGraphServiceResults',
                results_dict=parse_dict.get('results_dict')
            )

            return results

        return {}

from vital_ai_vitalsigns.service.graph.memory_graph_service import MemoryGraphService
from vital_ai_vitalsigns.service.vital_service import VitalService
from vital_ai_vitalsigns.vitalsigns import VitalSigns

from kgraphservice.kgraph_service import KGraphService


class KGraphServiceManagerMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class KGraphServiceManager(metaclass=KGraphServiceManagerMeta):
    def __init__(self):
        self.service_map = {}
        self.memory_service_map = {}
        vs = VitalSigns()

        vs_mgr = vs.get_vitalservice_manager()
        # add services to map based on vitalsigns config

    def get_kgraphservice_list(self):
        return self.service_map.keys()

    def get_kgraphservice_memory_list(self):
        return self.memory_service_map.keys()

    def get_kgraphservice(self, kgraphservice_name: str):

        if kgraphservice_name in self.memory_service_map:
            return self.memory_service_map[kgraphservice_name]

        if kgraphservice_name in self.service_map:
            return self.service_map[kgraphservice_name]

        return None

    # add kgraph memory service (dynamically added)

    def add_kgraphservice_memory(self, kgraphservice_name: str):

        memory_graph_service = MemoryGraphService()

        vital_service = VitalService(
            vitalservice_name=kgraphservice_name,
            graph_service=memory_graph_service)

        kgraph_service = KGraphService(vital_service=vital_service)

        self.memory_service_map[kgraphservice_name] = kgraph_service
        return kgraph_service

    def remove_kgraphservice_memory(self, kgraphservice_name: str):

        if kgraphservice_name in self.memory_service_map:
            del self.memory_service_map[kgraphservice_name]
            return True

        return False


    # remove kgraph memory service (dynamically added)




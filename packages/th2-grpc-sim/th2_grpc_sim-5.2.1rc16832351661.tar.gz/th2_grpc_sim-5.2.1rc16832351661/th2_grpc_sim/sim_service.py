from . import sim_pb2_grpc as importStub

class SimService(object):

    def __init__(self, router):
        self.connector = router.get_connection(SimService, importStub.SimStub)

    def removeRule(self, request, timeout=None, properties=None):
        return self.connector.create_request('removeRule', request, timeout, properties)

    def getRulesInfo(self, request, timeout=None, properties=None):
        return self.connector.create_request('getRulesInfo', request, timeout, properties)

    def getRelatedRules(self, request, timeout=None, properties=None):
        return self.connector.create_request('getRelatedRules', request, timeout, properties)

    def touchRule(self, request, timeout=None, properties=None):
        return self.connector.create_request('touchRule', request, timeout, properties)
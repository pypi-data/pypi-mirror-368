from . import sim_template_pb2_grpc as importStub

class SimTemplateService(object):

    def __init__(self, router):
        self.connector = router.get_connection(SimTemplateService, importStub.SimTemplateStub)

    def createRuleFixSecurity(self, request, timeout=None, properties=None):
        return self.connector.create_request('createRuleFixSecurity', request, timeout, properties)

    def createDemoRule(self, request, timeout=None, properties=None):
        return self.connector.create_request('createDemoRule', request, timeout, properties)

    def createRuleFix(self, request, timeout=None, properties=None):
        return self.connector.create_request('createRuleFix', request, timeout, properties)

    def createDemoRuleCancelReplace(self, request, timeout=None, properties=None):
        return self.connector.create_request('createDemoRuleCancelReplace', request, timeout, properties)
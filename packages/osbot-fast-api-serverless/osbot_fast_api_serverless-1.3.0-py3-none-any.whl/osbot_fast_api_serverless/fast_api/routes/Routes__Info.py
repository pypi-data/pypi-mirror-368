from osbot_fast_api.api.Fast_API_Routes      import Fast_API_Routes
from osbot_fast_api_serverless.utils.Version import version__osbot_fast_api_serverless

ROUTES_PATHS__INFO = ['/info/version']

class Routes__Info(Fast_API_Routes):
    tag :str = 'info'


    def version(self):
        return {'version': version__osbot_fast_api_serverless}

    
    def setup_routes(self):
        self.add_route_get(self.version)


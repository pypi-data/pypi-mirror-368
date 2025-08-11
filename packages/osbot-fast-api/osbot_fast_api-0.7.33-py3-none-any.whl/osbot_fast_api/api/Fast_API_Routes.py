from fastapi                                import APIRouter, FastAPI
from osbot_utils.type_safe.Type_Safe        import Type_Safe
from osbot_utils.decorators.lists.index_by  import index_by


class Fast_API_Routes(Type_Safe):       # refactor to Fast_API__Routes
    router : APIRouter
    app    : FastAPI = None
    prefix : str
    tag    : str

    def __init__(self, **kwargs):
        from osbot_utils.utils.Str import str_safe
        from osbot_utils.utils.Misc import lower

        super().__init__(**kwargs)
        self.prefix = f'/{lower(str_safe(self.tag))}'

    def add_route(self,function, methods):
        path = '/' + function.__name__.replace('_', '-')
        self.router.add_api_route(path=path, endpoint=function, methods=methods)
        return self

    def add_route_delete(self, function):
        return self.add_route(function=function, methods=['DELETE'])

    def add_route_get(self, function):
        return self.add_route(function=function, methods=['GET'])

    def add_route_post(self, function):
        return self.add_route(function=function, methods=['POST'])

    def add_route_put(self, function):
        return self.add_route(function=function, methods=['PUT'])

    def fast_api_utils(self):
        from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils
        return Fast_API_Utils(self.app)

    @index_by
    def routes(self):
        return self.fast_api_utils().fastapi_routes(router=self.router)

    def routes_methods(self):
        return list(self.routes(index_by='method_name'))

    def routes_paths(self):
        return list(self.routes(index_by='http_path'))

    def setup(self):
        self.setup_routes()
        self.app.include_router(self.router, prefix=self.prefix, tags=[self.tag])
        return self

    def setup_routes(self):     # overwrite this to add routes to self.router
        pass



    # def routes_list(self):
    #     items = []
    #     for route in self.routes():
    #         for http_methods in route.get('http_methods'):
    #             item = f'{http_methods:4} | {route.get("method_name"):14} | {route.get("http_path")}'
    #             items.append(item)
    #     return items
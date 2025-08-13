__author__ = "ziyan.yin"
__describe__ = ""

cimport cython

from starlette import _utils as starlette_utils
from starlette.datastructures import URL
from starlette.responses import RedirectResponse


cdef int find_params(unicode path):
    for i, ch in enumerate(path):
        if ch == "{":
            return i
    return -1


cdef int get_longest_common_prefix(unicode path, unicode node_path):
    cdef int i
    cdef int max_len = min(len(path), len(node_path))
    for i in range(max_len):
        if path[i] != node_path[i]:
            return i
    return max_len


@cython.no_gc
cdef class RouteNode:

    cdef readonly:
        unicode prefix
        list params_routes
        list static_routes
        dict children
    
    cdef public object parent

    def __cinit__(self, prefix: str):
        self.prefix = prefix
        self.params_routes = []
        self.static_routes = []
        self.children = {}
        self.parent = None
    
    def add_route(self, fullpath: str, handler: object):
        wild_child = False
        if (index := find_params(fullpath)) >= 0:
            wild_child = True
            path = fullpath[:index]
        else:
            path = fullpath
        insert_route(self, path, wild_child, handler)


cdef void insert_route(RouteNode node, unicode path, bint wild_child, object handler):
    if node.prefix == path:
        add_node(node, wild_child, handler)
        return

    cdef Py_UCS4 key = path.removeprefix(node.prefix)[0]
    if key not in node.children:
        add_child_node(node, key, path, wild_child, handler)
        return

    child_node = node.children[key]
    i = get_longest_common_prefix(child_node.prefix, path)
    longest_prefix = child_node.prefix[0: i]
    if i == len(child_node.prefix):
        insert_route(node.children[key], path, wild_child, handler)
        return
    next_node = RouteNode.__new__(RouteNode, longest_prefix)
    next_node.parent = node
    node.children[key] = next_node
    next_node.children[child_node.prefix[i]] = child_node
    child_node.parent = next_node
    insert_route(next_node, path, wild_child, handler)


cdef inline void add_child_node(RouteNode node, Py_UCS4 key, unicode path, bint wild_child, object handler):
    child = RouteNode.__new__(RouteNode, path)
    child.parent = node
    add_node(child, wild_child, handler)
    node.children[key] = child


cdef inline void add_node(RouteNode node, bint wild_child, object handler):
    if wild_child:
        node.params_routes.append(handler)
    else:
        node.static_routes.append(handler)


root_node = RouteNode.__new__(RouteNode, "")


cdef RouteNode search_node(unicode url):
    cdef RouteNode current_node = root_node
    cdef int n = len(url)
    cdef int i = get_longest_common_prefix(url, current_node.prefix)
    
    while i < n:
        key = url[i]
        if key not in current_node.children:
            break
        current_node = current_node.children[key]
        i = get_longest_common_prefix(url, current_node.prefix)

    return current_node


async def handle(scope, receive, send):
    router = scope["app"].router
    assert scope["type"] in ("http", "websocket", "lifespan")

    if "router" not in scope:
        scope["router"] = router

    if scope["type"] == "lifespan":
        await router.lifespan(scope, receive, send)
        return

    partial = None

    scope["path"] = route_path = starlette_utils.get_route_path(scope)
    leaf_node = search_node(route_path)

    if leaf_node.prefix == route_path:
        for route in leaf_node.static_routes:
            match, child_scope = route.matches(scope)
            if match.value == 2:
                scope.update(child_scope)
                await route.handle(scope, receive, send)
                return
            elif match.value == 1 and partial is None:
                partial = route
                partial_scope = child_scope
    else:
        current_node = leaf_node
        routes = current_node.params_routes
        while current_node.parent:
            for route in routes:
                match, child_scope = route.matches(scope)
                if match.value == 2:
                    scope.update(child_scope)
                    await route.handle(scope, receive, send)
                    return
                elif match.value == 1 and partial is None:
                    partial = route
                    partial_scope = child_scope
            current_node = current_node.parent

    if partial is not None:
        scope.update(partial_scope)
        await partial.handle(scope, receive, send)
        return

    if scope["type"] == "http" and router.redirect_slashes and route_path != "/":
        redirect_scope = dict(scope)
        if route_path.endswith("/"):
            redirect_scope["path"] = redirect_scope["path"].rstrip("/")
        else:
            redirect_scope["path"] = redirect_scope["path"] + "/"
        
        if leaf_node.prefix == redirect_scope["path"]:
            for route in leaf_node.static_routes:
                match, child_scope = route.matches(redirect_scope)
                if match.value != 0:
                    redirect_url = URL(scope=redirect_scope)
                    response = RedirectResponse(url=str(redirect_url))
                    await response(scope, receive, send)
                    return
        else:
            current_node = leaf_node
            routes = current_node.params_routes
            while current_node.parent:
                for route in routes:
                    if match.value != 0:
                        redirect_url = URL(scope=redirect_scope)
                        response = RedirectResponse(url=str(redirect_url))
                        await response(scope, receive, send)
                        return
                current_node = current_node.parent

    await router.default(scope, receive, send)


def install(app):
    for route in app.routes:
        root_node.add_route(route.path, route)

    app.router.middleware_stack = handle

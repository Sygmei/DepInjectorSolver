import graphlib
from typing import Callable


def get_function_direct_dependencies(function: Callable) -> dict[str, "Dependency"]:
    dependencies = {}
    if function.__defaults__ is None:
        return dependencies
    args_with_defaults = {
        arg: function.__defaults__[i]
        for i, arg in enumerate(function.__code__.co_varnames[-len(function.__defaults__):])
    }
    for arg_name, arg_value in args_with_defaults.items():
        if isinstance(arg_value, Dependency):
            dependencies[arg_name] = arg_value
    return dependencies

class Dependency:
    def __init__(self, function: Callable):
        self.function = function

    def get_name(self) -> str:
        return self.function.__name__

    def get_callable(self) -> Callable:
        return self.function

    def process_args_and_call(self, resolved_dependencies, **kwargs):
        direct_dependencies = get_function_direct_dependencies(self.function)
        used_args = {}
        for arg_name, arg_value in direct_dependencies.items():
            if arg_value.get_name() in resolved_dependencies:
                used_args[arg_name] = resolved_dependencies[arg_value.get_name()]
        function_args_names = self.function.__code__.co_varnames[:self.function.__code__.co_argcount]
        for kwarg_name, kwarg_value in kwargs.items():
            if kwarg_name in function_args_names:
                used_args[kwarg_name] = kwarg_value
        return self.function(**used_args)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


def get_function_dependencies(function: Callable) -> dict[str, Dependency]:
    dependencies = {}
    if function.__defaults__ is None:
        return dependencies
    args_with_defaults = {
        arg: function.__defaults__[i]
        for i, arg in enumerate(function.__code__.co_varnames[-len(function.__defaults__):])
    }
    for arg_value in args_with_defaults.values():
        if isinstance(arg_value, Dependency):
            dependencies[arg_value.get_name()] = arg_value
            dependencies.update(get_function_dependencies(arg_value.get_callable()))
    return dependencies

def get_dependency_resolution_order(function: Callable, graph: graphlib.TopologicalSorter | None = None) -> list:
    is_root = graph is None
    dependencies = get_function_dependencies(function)
    graph = graph if graph is not None else graphlib.TopologicalSorter()
    for dependency_name, dependency in dependencies.items():
        graph.add(function.__name__, dependency_name)
        get_dependency_resolution_order(dependency.get_callable(), graph)
    if is_root:
        return list(graph.static_order())



def resolve_dependencies(function: Callable, **kwargs):
    dependencies = get_function_dependencies(function)
    resolution_order = get_dependency_resolution_order(function)
    resolved_dependencies = {}
    for dependency_name in resolution_order:
        if dependency_name == function.__name__:
            continue
        resolved_dependencies[dependency_name] = dependencies[dependency_name].process_args_and_call(resolved_dependencies, **kwargs)
    return Dependency(function).process_args_and_call(resolved_dependencies, **kwargs)

def depends(function: Callable):
    return Dependency(function)

def requires_ten() -> int:
    print("Resolve requires_ten")
    return 10

def requires_twenty(ten: int = depends(requires_ten)):
    print("Resolve requires_twenty")
    return ten * 2

def requires_twenty_plus_a_plus_b(a: int, b: int, twenty: int = depends(requires_twenty)):
    print("Resolve requires_twenty_plus_a_plus_b")
    return twenty + a + b

def requires_multiple(a, b, complex: int = depends(requires_twenty_plus_a_plus_b), ten1: int = depends(requires_ten), ten2: int = depends(requires_ten), twenty1: int = depends(requires_twenty), twenty2: int = depends(requires_twenty)):
    print("Resolve requires_multiple", a, b, complex, ten1, ten2, twenty1, twenty2)
    return a + b + complex + ten1 + ten2 + twenty1 + twenty2

def main():
    result = resolve_dependencies(requires_multiple, a=50, b=30)
    print(result)

if __name__ == '__main__':
    main()

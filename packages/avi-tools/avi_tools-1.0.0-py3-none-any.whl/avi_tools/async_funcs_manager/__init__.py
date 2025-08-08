import time
import asyncio
from collections.abc import Callable
from typing import Any, Tuple, List, Dict
from contextlib import AbstractAsyncContextManager
# module async_funcs_manager

class CapsFunc:
    """
    Encapsulates a callable function along with its name, positional arguments, and keyword arguments.
    """

    def __init__(self, _name: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Initialize a CapsFunc instance.

        Parameters:
            _name (str): The name to associate with the function.
            func (Callable[..., Any]): The function to encapsulate.
            *args (Any): Positional arguments to pass when calling func.
            **kwargs (Any): Keyword arguments to pass when calling func.

        Raises:
            TypeError: If func is not callable.
            TypeError: If _name is not a string.
        """
        if not callable(func):
            raise TypeError(f"Provided func must be callable, got {type(func).__name__}")
        if not isinstance(_name, str):
            raise TypeError(f"Function name must be a string, got {type(_name).__name__}")

        self.__name: str = _name
        self.__func: Callable[..., Any] = func
        self.__args: List[Any] = list(args)
        self.__kwargs: Dict[str, Any] = dict(kwargs)

    def get(self) -> Tuple[str, Callable[..., Any], List[Any], Dict[str, Any]]:
        """
        Retrieve the stored function name, function object, positional arguments, and keyword arguments.

        Returns:
            Tuple[str, Callable[..., Any], List[Any], Dict[str, Any]]: (_name, func, args, kwargs)
        """
        return self.__name, self.__func, self.__args, self.__kwargs


class FuncsToAsync:
    """
    Container class to manage multiple CapsFunc instances and execute them asynchronously.
    """

    def __init__(self,/, *cfunc: CapsFunc) -> None:
        """
        Initialize the container with zero or more CapsFunc objects.

        Parameters:
            *cfunc (CapsFunc): One or more CapsFunc instances to add initially.

        Raises:
            TypeError: If any item in cfunc is not a CapsFunc instance.
        """
        self.__allfuncs: Dict[str, Tuple[Callable[..., Any], List[Any], Dict[str, Any]]] = {}
        for item in cfunc:
            if not isinstance(item, CapsFunc):
                raise TypeError(f"Expected CapsFunc instance, got {type(item).__name__}")
            name, func, args, kwargs = item.get()
            self.__allfuncs[name] = (func, args, kwargs)

    def __getattr__(self, item: str) -> Tuple[Callable[..., Any], List[Any], Dict[str, Any]]:
        """
        Provide attribute-like access to stored functions by their name.

        Parameters:
            item (str): The function name.

        Returns:
            Tuple[Callable[..., Any], List[Any], Dict[str, Any]]: (func, args, kwargs) if function is found.

        Raises:
            AttributeError: If function name does not exist.
        """
        if item in self.__allfuncs:
            return self.__allfuncs[item]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

    def add(self, cfunc: CapsFunc, force: bool = False) -> None:
        """
        Add a CapsFunc object to the container.

        Parameters:
            cfunc (CapsFunc): The CapsFunc instance to add.
            force (bool, optional): If True, overwrite existing function with same name. Default is False.

        Raises:
            TypeError: If cfunc is not a CapsFunc instance.
            KeyError: If function name already exists and force is False.
        """
        if not isinstance(cfunc, CapsFunc):
            raise TypeError(f"Expected CapsFunc instance, got {type(cfunc).__name__}")

        name, func, args, kwargs = cfunc.get()
        if name in self.__allfuncs:
            if force:
                self.__allfuncs[name] = (func, args, kwargs)
            else:
                raise KeyError(f"{name} already in {self}")
        else:
            self.__allfuncs[name] = (func, args, kwargs)

    async def __call__(self, name: str) -> Any:
        """
        Asynchronously execute the stored function identified by name.

        Parameters:
            name (str): The name of the function to execute.

        Returns:
            Any: The result of the function call.

        Raises:
            TypeError: If name is not a string.
            KeyError: If function name not found in the container.
        """
        if not isinstance(name, str):
            raise TypeError(f"Function name must be a string, got {type(name).__name__}")

        if name not in self.__allfuncs:
            raise KeyError(f"Function '{name}' not found in {self}")
        func, args, kwargs = self.__allfuncs[name]
        result = await asyncio.to_thread(func, *args, **kwargs)
        return result

    def __str__(self) -> str:
        """
        Return string representation listing all stored function names.

        Returns:
            str: Comma-separated list of function names enclosed in brackets.
        """
        funcs = ', '.join(self.__allfuncs.keys())
        return f"[{funcs}]"

    def __repr__(self) -> str:
        """
        Return unambiguous representation with class name and function names.

        Returns:
            str: Representation including class name and function names.
        """
        return f"FuncsToAsync({list(self.__allfuncs.keys())})"

    def __contains__(self, name: str) -> bool:
        """
        Check if a function with the given name exists.

        Parameters:
            name (str): Function name to check.

        Returns:
            bool: True if function exists, False otherwise.
        """
        return name in self.__allfuncs

    def names(self) -> List[str]:
        """
        Return list of all stored function names.

        Returns:
            List[str]: List of function names.
        """
        return list(self.__allfuncs.keys())

class AsyncRunner(AbstractAsyncContextManager):
    """
    Context manager for running multiple registered functions concurrently
    using FuncsToAsync, leveraging asyncio and run_in_executor.

    Parameters:
        funcs (FuncsToAsync): Instance containing registered functions.

    Example:
        with await AsyncRunner(funcs) as runner:
            results = await runner.run_all()
    """
    def __init__(self, funcs: FuncsToAsync):
        if not isinstance(funcs, FuncsToAsync):
            raise TypeError(f"Expected FuncsToAsync, got {type(funcs).__name__}")
        self.funcs = funcs
        self.loop = None

    async def __aenter__(self):
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass  # no cleanup required here

    async def run_all(self):
        """
        Run all registered functions concurrently using run_in_executor.
        Returns:
            dict[str, Any]: Mapping from function name to result.
        """
        tasks = {}
        for name in self.funcs.names():
            func, args, kwargs = getattr(self.funcs, name)
            task = self.loop.run_in_executor(None, func, *args, **kwargs)
            tasks[name] = task

        # Await all tasks
        results = await asyncio.gather(*tasks.values())
        return dict(zip(tasks.keys(), results))


if __name__ == "__main__":

    def slow_add(a: int, b: int) -> int:
        time.sleep(1)
        return a + b

    def say_hello(name: str) -> str:
        time.sleep(1)
        return f"Hello, {name}!"

    f1 = CapsFunc("add", slow_add, 3, 4)
    f2 = CapsFunc("hello", say_hello, name="Twill")

    funcs = FuncsToAsync(f1, f2)

    print(funcs)  # [add, hello]
    print(repr(funcs))  # FuncsToAsync(['add', 'hello'])

    async def main() -> None:
        result1 = await funcs("add")
        result2 = await funcs("hello")
        print(result1)  # 7
        print(result2)  # Hello, Twill

        try:
            await funcs("not_exist")
        except KeyError as e:
            print(e)

        # Additional input validation tests

        try:
            funcs.add("not a CapsFunc")  # type: ignore
        except TypeError as e:
            print("Expected TypeError:", e)

        try:
            bad_func = CapsFunc(123, slow_add)
        except TypeError as e:
            print("Expected TypeError:", e)

        try:
            await funcs(123)  # type: ignore
        except TypeError as e:
            print("Expected TypeError:", e)

        try:
            funcs.add(CapsFunc("add", slow_add, 1, 2), force=False)
        except KeyError as e:
            print("Expected KeyError on duplicate add:", e)

        # Force overwrite test
        funcs.add(CapsFunc("add", slow_add, 5, 6), force=True)
        result3 = await funcs("add")
        print("After force update, add returns:", result3)

    asyncio.run(main())

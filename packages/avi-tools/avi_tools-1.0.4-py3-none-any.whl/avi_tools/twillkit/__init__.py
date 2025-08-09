from typing import Callable
from contextlib import contextmanager
import traceback
import sys
import os
from tkinter import filedialog
# module twillkit

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    ORANGE = "\033[38;2;255;165;0m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    END = "\033[0m"


class Monoid:
    """
    Monoid class to hold a collection of values with functional utilities
    like map, filter, group by type, and more.
    """
    def __init__(self, *value):
        self.__value = value
        self.__index = 0

    def __repr__(self):
        return f"Monoid({self.__value})"

    def __iter__(self):
        self.__index = 0
        return self

    def __contains__(self, item):
        return item in self.__value

    def __add__(self, other: "Monoid"):
        return self.combine(other)

    def __next__(self):
        if self.__index >= len(self.__value):
            raise StopIteration
        value = self.__value[self.__index]
        self.__index += 1
        return value

    def __length_hint__(self):
        return len(self.__value) - self.__index

    def __eq__(self, other):
        return isinstance(other, Monoid) and self.__value == other.__value

    def __len__(self):
        return len(self.__value)

    def __call__(self, func: Callable, *args, **kwargs):
        return self.map(func, *args, **kwargs)

    def map(self, func: Callable, *args, **kwargs):
        return Monoid(*[func(item, *args, **kwargs) for item in self.__value])

    def map_type(self, target_type: type, func: Callable, *args, **kwargs) -> "Monoid":
        return Monoid(*[
            func(item, *args, **kwargs) if isinstance(item, target_type) else item
            for item in self.__value
        ])

    def combine(self, other: "Monoid"):
        if not isinstance(other, Monoid):
            raise TypeError("Expected Monoid instance")
        return Monoid(*(self.__value + other.__value))

    @staticmethod
    def identity():
        return Monoid()

    def group_by_type(self) -> dict:
        result = {}
        for item in self.__value:
            type_name = type(item).__name__
            result.setdefault(type_name, []).append(item)
        return result

    def split_by_type(self) -> dict[type, "Monoid"]:
        result = {}
        for item in self.__value:
            t = type(item)
            if t not in result:
                result[t] = []
            result[t].append(item)
        return {t: Monoid(*items) for t, items in result.items()}

    def value(self):
        return self.__value


class Infix:
    """
    Enables infix notation for functions using the | operator.
    Example: 3 |add| 5
    """
    def __init__(self, fuc: Callable):
        self.func = fuc

    def __call__(self, value1, value2):
        return self.func(value1, value2)

    def __ror__(self, other: "Infix"):
        return Infix(lambda x: self.func(other, x))

    def __or__(self, other: "Infix"):
        return self.func(other)


@contextmanager
def catch_exceptions():
    """
    Context manager to catch and display exceptions with line number and color formatting.
    """
    try:
        print(f"{Colors.BLUE}start of {Colors.ORANGE}try{Colors.END}:{Colors.ORANGE} except{Colors.END}:{Colors.BLUE} blocke{Colors.END}")
        yield
    except Exception as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        line_number = tb[-1].lineno
        print(f"{Colors.RED}{e}{Colors.YELLOW} at line:{Colors.PURPLE}{line_number}{Colors.END}")
    else:
        print(f"{Colors.GREEN}No Errors{Colors.END}")
    finally:
        print(f"{Colors.BLUE}end of {Colors.ORANGE}try{Colors.END}:{Colors.ORANGE} except{Colors.END}:{Colors.BLUE} blocke{Colors.END}")


class CreateFolderForFileCreation:
    """
    Creates a directory and allows safe file creation within it using a context manager.
    Prevents overwriting existing folders or files.
    """
    def __init__(self, dir_name: str, dir_path: str = os.getcwd()):
        self.dir_full_path = os.path.join(dir_path, dir_name)
        if os.path.exists(self.dir_full_path):
            raise FileExistsError(
                f"{Colors.RED}Folder {Colors.BLUE}{dir_name}{Colors.RED} already exist in {Colors.BLUE}{dir_path}{Colors.END}")
        os.mkdir(self.dir_full_path)
        print(f"{Colors.BLUE}folder {Colors.GREEN}{dir_name} {Colors.BLUE}created in \n{Colors.YELLOW}{dir_path}{Colors.END}")

    @contextmanager
    def __call__(self, file_name: str, mode: str = "w"):
        file = None
        try:
            file_path = os.path.join(self.dir_full_path, file_name)
            if os.path.exists(file_path):
                raise FileExistsError(
                    f"{Colors.RED}File {Colors.BLUE}{file_name}{Colors.RED} already exist in {Colors.BLUE}{self.dir_full_path}{Colors.END}")
            file = open(file_path, mode)
            yield file
        except Exception as e:
            tb = traceback.extract_tb(sys.exc_info()[2])
            line_number = tb[-1].lineno
            print(f"{Colors.RED}{e}{Colors.YELLOW} at line:{Colors.PURPLE}{line_number}{Colors.END}")
        finally:
            if file:
                file.close()


class InteractivePathSelectFileCreation:
    """
    Allows the user to choose a folder using a dialog and safely create a file inside it.
    Prevents overwriting existing files.
    """
    def __init__(self):
        self.dir_full_path = filedialog.askdirectory()

    @contextmanager
    def __call__(self, file_name: str, mode: str = "w"):
        file = None
        try:
            file_path = os.path.join(self.dir_full_path, file_name)
            if os.path.exists(file_path):
                raise FileExistsError(
                    f"{Colors.RED}File {Colors.BLUE}{file_name}{Colors.RED} already exist in {Colors.BLUE}{self.dir_full_path}{Colors.END}")
            file = open(file_path, mode)
            yield file
        except Exception as e:
            tb = traceback.extract_tb(sys.exc_info()[2])
            line_number = tb[-1].lineno
            print(f"{Colors.RED}{e}{Colors.YELLOW} at line:{Colors.PURPLE}{line_number}{Colors.END}")
        finally:
            if file:
                file.close()

if __name__ == "__main__":
    # =======================
    # Usage Demonstrations
    # =======================

    # Demonstration 1: Using Monoid
    m = Monoid(1, 2, 3, 4)
    print("Original Monoid:", m)

    # Map all elements to their square
    squared = m.map(lambda x: x * x)
    print("Squared Monoid:", squared)

    # Filter only even numbers (demonstration via list)
    even_items = [x for x in m if x % 2 == 0]
    print("Even items:", even_items)

    # Group by type
    mixed = Monoid(1, "hello", 3.14, True)
    grouped = mixed.group_by_type()
    print("Grouped by type:", grouped)


    # Demonstration 2: Using Infix operator

    def add_nums(x, y):
        result = x + y
        print(f"{x} + {y} = {result}")
        return result


    def subtract_nums(x, y):
        result = x - y
        print(f"{x} - {y} = {result}")
        return result


    add = Infix(add_nums)
    sub = Infix(subtract_nums)

    # Using infix operators
    result1 = 5 | add | 3
    result2 = 10 | sub | 4

    # Demonstration 3: Using catch_exceptions context manager
    with catch_exceptions():
        print("Attempting to divide by zero")
        x = 1 / 0

    # Demonstration 4: Using CreateFolderForFileCreation
    #----------------------------------------------------------
    # This will create a folder and file safely (uncomment to run)

    # folder = CreateFolderForFileCreation("example_folder")
    # with folder("test.txt") as f:
    #     f.write("Hello from test.txt")

    # Demonstration 5: Using InteractivePathSelectFileCreation
    #----------------------------------------------------------
    # This will prompt a folder selection (uncomment to run)

    # creator = InteractivePathSelectFileCreation()
    # with creator("chosen_path_file.txt") as f:
    #     f.write("This file was created in a chosen folder")
from .async_funcs_manager import CapsFunc,FuncsToAsync,AsyncRunner
from .twillkit import Monoid, Colors, Infix, InteractivePathSelectFileCreation ,CreateFolderForFileCreation ,catch_exceptions
from .variabledb import VariableDB

# avi_tools/__init__.py

def help():
    import textwrap

    menu = {
        "1": {
            "title": "run_async_functions",
            "desc": "Run multiple async functions concurrently.",
            "example": textwrap.dedent("""
                import asyncio
                from avi_tools.async_function_manager import run_async_functions

                async def say_hello():
                    print("Hello")

                async def say_world():
                    print("World")

                asyncio.run(run_async_functions([say_hello, say_world]))
            """)
        },
        "2": {
            "title": "VarDB",
            "desc": "In-memory variable key-value database.",
            "example": textwrap.dedent("""
                from avi_tools.variable_database import VarDB

                db = VarDB()
                db.set("name", "Avi")
                print(db.get("name"))  # Output: Avi
            """)
        },
        "3": {
            "title": "clear_terminal",
            "desc": "Clear the terminal screen.",
            "example": textwrap.dedent("""
                from avi_tools.terminal_utils import clear_terminal

                clear_terminal()
            """)
        },
        "4": {
            "title": "print_with_color",
            "desc": "Print text in color in the terminal.",
            "example": textwrap.dedent("""
                from avi_tools.terminal_utils import print_with_color

                print_with_color("Hello", "green")
            """)
        }
    }

    while True:
        print("\navi_tools Help Menu")
        print("====================")
        for key, value in menu.items():
            print(f"{key}. {value['title']} – {value['desc']}")
        print("0. Exit")

        choice = input("\nEnter a number to get help on a topic (0 to exit): ")

        if choice == "0":
            print("Exiting help.")
            break
        elif choice in menu:
            selected = menu[choice]
            print(f"\n--- {selected['title']} ---")
            print(f"{selected['desc']}\n")
            print("Example usage:")
            print(selected['example'])
            input("\nPress Enter to return to the menu...")
        else:
            print("Invalid choice. Please try again.")


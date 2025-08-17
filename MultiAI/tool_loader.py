import importlib
import os
import inspect

def load_tools_from_directory(directory='tools'):
    """
    Dynamically loads tools from a directory.
    Returns a dictionary where keys are tool names and values are another
    dictionary containing the function object, its signature, and its docstring.
    """
    tool_functions = {}
    for filename in os.listdir(directory):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = f"{directory}.{filename[:-3]}"
            module = importlib.import_module(module_name)
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith('_'):
                    # Get the function signature and docstring
                    signature = str(inspect.signature(func))
                    docstring = func.__doc__.strip() if func.__doc__ else "No description available."
                    
                    tool_functions[name] = {
                        'func': func,
                        'signature': signature,
                        'docstring': docstring
                    }
    return tool_functions
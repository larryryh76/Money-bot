import importlib

def get_parser(site):
    """Dynamically loads the parser for a given site."""
    try:
        module_name = f"parsers.{site.replace('.', '_')}"
        class_name = "".join([s.capitalize() for s in site.split('.')]) + "Parser"
        module = importlib.import_module(module_name)
        return getattr(module, class_name)()
    except (ImportError, AttributeError):
        return None

from importlib import import_module


def load_class(class_name: str, *module_names: str):
    """Carrega uma classe futura sem impedir a execução dos testes atuais."""
    for module_name in module_names:
        try:
            module = import_module(module_name)
        except ModuleNotFoundError:
            continue
        model_class = getattr(module, class_name, None)
        if model_class is not None:
            return model_class
    return None

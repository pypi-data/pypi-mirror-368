def decorate_all_methods(decorator: callable, exclude=None, exclude_startswith: str = None):
    if exclude is None:
        exclude = []

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and attr not in exclude and (
                    exclude_startswith and not attr.startswith(exclude_startswith)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate

class NoInstantiable:
    """Class that can't be instantiable"""
    def __new__(cls) -> None:
        raise SyntaxError(f'Class "{cls.__name__}" is not instantiable')

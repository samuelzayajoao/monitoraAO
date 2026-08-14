def get_list_secret_value(*args: list | tuple):
    return [element.get_secret_value() for element in args]

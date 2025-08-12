from types import LambdaType


def rgb(r: int, g: int, b: int) -> LambdaType:
    return lambda string: f"\033[38;2;{r};{g};{b}m{string}\033[0m"

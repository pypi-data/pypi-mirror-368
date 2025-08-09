# super_x/random.py
import random
from superbeta.core import Tensor

_seed = 1234
def seed(s: int):
    global _seed
    _seed = int(s)
    random.seed(_seed)

def rand(shape):
    """Genera tensor con valores [0,1). shape: tupla."""
    if not isinstance(shape, tuple):
        raise TypeError("shape debe ser tupla")
    def nested(s):
        if not s:
            return random.random()
        return [nested(s[1:]) for _ in range(s[0])]
    return Tensor(nested(shape))

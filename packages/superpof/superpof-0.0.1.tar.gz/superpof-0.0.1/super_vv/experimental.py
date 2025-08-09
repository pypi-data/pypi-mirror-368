# super_vv/experimental.py
"""
Funciones experimentales: pequeño 'jit' que compila expresiones Python simples
en funciones vectorizadas sobre Tensor.flat. Sólo para experimentos.
"""
from superbeta.core import Tensor

def simple_jit(py_expr: str):
    """
    Devuelve una función que aplica py_expr (e.g. "x*2 + 3") a cada elemento.
    IMPORTANTE: expr debe usar variable 'x' y operaciones seguras.
    """
    code = compile(py_expr, "<jit>", "eval")
    def func(tensor: Tensor):
        out_flat = [eval(code, {"x": v}) for v in tensor.flat]
        out = Tensor(out_flat, requires_grad=tensor.requires_grad)
        out.shape = tensor.shape
        # backward: derivative is evaluated numerically (aprox) => experimental
        def _backward():
            if out.grad is None:
                return
            if tensor.requires_grad:
                tensor._ensure_grad()
                # derivada numérica pequeña (very naive)
                eps = 1e-6
                for i, v in enumerate(tensor.flat):
                    # central difference
                    f1 = eval(code, {"x": v + eps})
                    f0 = eval(code, {"x": v - eps})
                    d = (f1 - f0) / (2 * eps)
                    tensor.grad[i] += out.grad[i] * d
        out._backward = _backward
        return out
    return func

# super_x/linalg.py
from superbeta.core import Tensor
from superbeta.utils import unflatten, flatten

def transpose(tensor: Tensor):
    if len(tensor.shape) != 2:
        raise ValueError("transpose soporta 2D sólo")
    m, n = tensor.shape
    A = unflatten(tensor.flat, tensor.shape)
    T = [[A[i][j] for i in range(m)] for j in range(n)]
    out = Tensor(T, requires_grad=tensor.requires_grad)
    return out

def solve_linear(A: Tensor, b: Tensor):
    """
    Resolver A x = b por eliminación Gaussiana (para matrices pequeñas).
    A: Tensor 2D (n,n), b: Tensor (n,) o (n,1)
    Retorna Tensor x.
    Nota: no es robusto ni optimizado (apoyo experimental).
    """
    if len(A.shape) != 2:
        raise ValueError("A debe ser 2D")
    n, n2 = A.shape
    if n != n2:
        raise ValueError("A debe ser cuadrada")
    # convertir a floats
    M = [row[:] for row in unflatten(A.flat, A.shape)]
    bb = unflatten(b.flat, b.shape)
    # aplanamos bb a vector
    if isinstance(bb[0], list):
        bb = [r[0] for r in bb]
    # Eliminación Gaussiana (in-place)
    for i in range(n):
        # pivot simple
        pivot = M[i][i]
        if abs(pivot) < 1e-12:
            # buscar fila con pivot no nulo y swap
            for k in range(i+1, n):
                if abs(M[k][i]) > 1e-12:
                    M[i], M[k] = M[k], M[i]
                    bb[i], bb[k] = bb[k], bb[i]
                    pivot = M[i][i]
                    break
            else:
                raise ValueError("Matriz singular o pivot pequeño")
        # normalizar fila
        factor = pivot
        M[i] = [v / factor for v in M[i]]
        bb[i] = bb[i] / factor
        # eliminar otras filas
        for r in range(n):
            if r == i:
                continue
            factor2 = M[r][i]
            if factor2 != 0.0:
                M[r] = [M[r][c] - factor2 * M[i][c] for c in range(n)]
                bb[r] = bb[r] - factor2 * bb[i]
    return Tensor([[v] for v in bb])


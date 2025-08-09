# super_vv/nn.py
from superbeta.core import Tensor
from superbeta.ops import array
import random
import math

class Linear:
    """Capa linear simple: output = x @ W^T + b (x: batch x in_features)"""
    def __init__(self, in_features, out_features, bias=True):
        self.in_features = in_features
        self.out_features = out_features
        self.W = Tensor([[ (random.random()*2-1) * math.sqrt(2/in_features) for _ in range(in_features)] for __ in range(out_features)], requires_grad=True)
        self.b = Tensor([[0.0] for _ in range(out_features)], requires_grad=True) if bias else None

    def __call__(self, x: Tensor):
        # x: (batch, in_features)
        # W: (out_features, in_features) -> queremos x @ W.T -> (batch, out_features)
        Wt = Tensor([list(col) for col in zip(*W.numpy())]) if False else None
        # Reuse matmul: convert W to shape (in_features, out_features) by transpose
        # easier: compute manually
        X = unflatten(x.flat, x.shape)
        W = unflatten(self.W.flat, self.W.shape)
        batch = x.shape[0]
        out = []
        for i in range(batch):
            row = []
            for j in range(self.out_features):
                s = sum(X[i][k] * W[j][k] for k in range(self.in_features))
                if self.b is not None:
                    s += self.b.flat[j]
                row.append(s)
            out.append(row)
        return Tensor(out, requires_grad=x.requires_grad or self.W.requires_grad or (self.b is not None and self.b.requires_grad))

# Optimizer (SGD)
class SGD:
    def __init__(self, params, lr=1e-2):
        self.params = list(params)
        self.lr = lr

    def step(self):
        for p in self.params:
            if p.grad is None:
                continue
            for i in range(len(p.flat)):
                p.flat[i] -= self.lr * p.grad[i]

    def zero_grad(self):
        for p in self.params:
            if p.grad is not None:
                for i in range(len(p.grad)):
                    p.grad[i] = 0.0

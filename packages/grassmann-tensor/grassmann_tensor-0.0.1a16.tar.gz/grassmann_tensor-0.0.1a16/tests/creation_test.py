import pytest
import torch
from grassmann_tensor import GrassmannTensor


def test_creation() -> None:
    x = GrassmannTensor((False, False), ((2, 2), (1, 3)), torch.randn([4, 4]))
    with pytest.raises(AssertionError):
        x = GrassmannTensor((False, False, False), ((2, 2), (1, 3)), torch.randn([4, 4]))
    with pytest.raises(AssertionError):
        x = GrassmannTensor((False, False), ((2, 2), (1, 3), (3, 1)), torch.randn([4, 4]))
    with pytest.raises(AssertionError):
        x = GrassmannTensor((False, False), ((2, 2), (1, 1)), torch.randn([4, 4]))

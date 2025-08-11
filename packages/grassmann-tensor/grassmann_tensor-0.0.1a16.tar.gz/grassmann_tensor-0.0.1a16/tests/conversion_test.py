import typing
import pytest
import torch
from grassmann_tensor import GrassmannTensor


@pytest.fixture()
def x() -> GrassmannTensor:
    return GrassmannTensor((False, False), ((2, 2), (1, 3)), torch.randn([4, 4]))


@pytest.mark.parametrize("dtype_arg", ["position", "keyword", "none"])
@pytest.mark.parametrize("device_arg", ["position", "keyword", "none"])
@pytest.mark.parametrize("device_format", ["object", "string"])
def test_conversion(
    x: GrassmannTensor,
    dtype_arg: typing.Literal["position", "keyword", "none"],
    device_arg: typing.Literal["position", "keyword", "none"],
    device_format: typing.Literal["object", "string"],
) -> None:
    args: list[typing.Any] = []
    kwargs: dict[str, typing.Any] = {}

    device = torch.device("cpu") if device_format == "object" else "cpu"
    match device_arg:
        case "position":
            args.append(device)
        case "keyword":
            kwargs["device"] = device
        case _:
            pass

    match dtype_arg:
        case "position":
            args.append(torch.complex128)
        case "keyword":
            kwargs["dtype"] = torch.complex128
        case _:
            pass

    if len(args) <= 1:
        y = x.to(*args, **kwargs)


def test_conversion_invalid_type(x: GrassmannTensor) -> None:
    with pytest.raises(TypeError):
        x.to(2333)  # type: ignore[arg-type]


def test_conversion_duplicated_value(x: GrassmannTensor) -> None:
    with pytest.raises(AssertionError):
        x.to(torch.device("cpu"), device=torch.device("cpu"))
    with pytest.raises(AssertionError):
        x.to(torch.complex128, dtype=torch.complex128)
    with pytest.raises(AssertionError):
        x.to("cpu", device=torch.device("cpu"))

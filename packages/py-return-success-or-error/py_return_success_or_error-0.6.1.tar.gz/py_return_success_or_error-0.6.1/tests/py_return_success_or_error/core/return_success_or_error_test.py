from py_return_success_or_error import (
    ErrorGeneric,
    ErrorReturn,
    ReturnSuccessOrError,
    SuccessReturn,
)


class OtherReturn(ReturnSuccessOrError):

    def __str__(self) -> str:
        """Retorna a representação do success."""
        return f'OtherReturn: {self.result}'


def setReturnSuccessOrError(result: bool) -> ReturnSuccessOrError[str]:
    if result:
        return SuccessReturn[str]('Teste ok')
    else:
        return ErrorReturn[str](ErrorGeneric(message='Teste erro'))


def testInstance():
    result_success_bool = SuccessReturn[bool](False)
    assert not result_success_bool.result
    assert str(result_success_bool) == 'Success: False'
    result_error_bool = ErrorReturn[bool](
        ErrorGeneric(message='Teste de erro'))
    assert result_error_bool.result.message == 'Teste de erro'
    assert str(result_error_bool) == 'Error: ErrorGeneric - Teste de erro'

    result = setReturnSuccessOrError(True)
    print()

    if isinstance(result, SuccessReturn):
        assert result.result == 'Teste ok'
    else:
        assert False


def testSuccessNone():
    try:
        teste_none = SuccessReturn[str](None)
        result = teste_none.result
        print()
        print('#################')
        print(result)
        assert False
    except ValueError as e:
        assert str(e) == "Não pode retornar um valor nulo."


def testErrorNone():
    try:
        teste_none = ErrorReturn[str](None)
        result = teste_none.result
        print(result)
        assert False
    except ValueError as e:
        assert str(e) == "Não pode retornar um valor nulo."


def testOtherReturn():
    try:
        teste_none = OtherReturn()
        result = teste_none.result
        print(result)
        assert False
    except ValueError as e:
        assert str(e) == "SubClass Invalida."

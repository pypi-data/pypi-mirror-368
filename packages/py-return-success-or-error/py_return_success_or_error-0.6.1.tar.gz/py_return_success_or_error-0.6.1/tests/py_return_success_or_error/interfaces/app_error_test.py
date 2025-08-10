
from py_return_success_or_error import AppError, ErrorGeneric
from tests.helpers import ErrorTestData


def testInstanciaAppError():
    erro_generic = ErrorGeneric(message='teste erro ErrorGeneric')
    erro_test = ErrorTestData(message='teste erro ErrorTest', status_code=400)
    erro_test2 = ErrorTestData(message='teste erro ErrorTest', status_code=400)
    erro_test2_copy = ErrorTestData(
        message='teste erro ErrorTest', status_code=400)

    assert isinstance(erro_generic, AppError)
    assert erro_generic.message == 'teste erro ErrorGeneric'
    assert isinstance(erro_test, ErrorTestData)
    assert erro_test.message == 'teste erro ErrorTest'
    assert erro_test.status_code == 400
    assert erro_test2_copy == erro_test2
    assert str(erro_generic) == "ErrorGeneric - teste erro ErrorGeneric"

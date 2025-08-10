
from py_return_success_or_error import NoParams, ParametersReturnResult
from tests.helpers import (
    ErrorTestData,
    InfoParametros,
    PessoaParametros,
)


def testNoParams() -> None:
    no_params = NoParams()
    no_params_error_test = NoParams(ErrorTestData(
        message='teste erro ErrorTest', status_code=400))
    assert str(
        no_params) == "NoParams(error=ErrorGeneric(message='General Error'))"
    assert isinstance(no_params, ParametersReturnResult)
    assert no_params.error.message == 'General Error'
    assert isinstance(no_params_error_test, ParametersReturnResult)
    assert isinstance(no_params_error_test.error, ErrorTestData)
    error_test: ErrorTestData = no_params_error_test.error
    if isinstance(error_test, ErrorTestData):
        assert error_test.status_code == 400  # pylint: disable=no-member
        assert error_test.message == 'teste erro ErrorTest'
    else:
        assert False


def testParametrosGerais():
    tete_params = PessoaParametros(nome='teste', idade=20, error=ErrorTestData(message='teste erro ErrorTest', status_code=400))

    tete_params_gerais = InfoParametros(
        error=ErrorTestData(message='teste erro ErrorTest', status_code=400),
        informacoes={'teste': 'teste'},
    )
    assert str(
        tete_params) == "TestesParametros(nome=teste, idade=20, error=ErrorTestData - teste erro ErrorTest)"
    assert str(
        tete_params_gerais) == "TestesParametrosGerais(informaçõess={'teste': 'teste'}, error=ErrorTestData - teste erro ErrorTest)"
    assert isinstance(tete_params, ParametersReturnResult)
    assert isinstance(tete_params_gerais, ParametersReturnResult)
    assert isinstance(tete_params.error, ErrorTestData)
    assert isinstance(tete_params_gerais.error, ErrorTestData)
    assert tete_params.error.status_code == 400
    assert tete_params.error.message == 'teste erro ErrorTest'
    assert tete_params_gerais.error.status_code == 400  # pylint: disable=no-member
    assert tete_params_gerais.error.message == 'teste erro ErrorTest'
    assert tete_params.nome == 'teste'
    assert tete_params.idade == 20
    assert tete_params_gerais.informacoes == {'teste': 'teste'}

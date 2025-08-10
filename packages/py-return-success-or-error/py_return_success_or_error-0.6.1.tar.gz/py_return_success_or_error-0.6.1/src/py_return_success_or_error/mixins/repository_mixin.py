from py_return_success_or_error.imports import (
    Datasource,
    ErrorReturn,
    ParametersReturnResult,
    ReturnSuccessOrError,
    SuccessReturn,
    TypeVar,
)

TypeDatasource = TypeVar('TypeDatasource')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class RepositoryMixin():
    """
    Mixin para fornecer funcionalidade de acesso a fontes de dados (DataSources).

    Esta mixin implementa a lógica para executar um `Datasource` e tratar o resultado,
    retornando um `SuccessReturn` com o resultado do `Datasource` em caso de sucesso,
    ou um `ErrorReturn` com o erro do parâmetro em caso de exceção.

    Atributos:
        Nenhum.

    Métodos:
        _resultDatasource(parameters, datasource): Executa o `Datasource` e retorna o resultado.
    """

    def _resultDatasource(
        self,
        parameters: TypeParameters,
        datasource: Datasource[TypeDatasource, TypeParameters]
    ) -> ReturnSuccessOrError[TypeDatasource]:
        """
        Executa um `Datasource` e retorna o resultado encapsulado em um `ReturnSuccessOrError`.

        Este método recebe um objeto de parâmetros e um `Datasource`, executa o `Datasource`
        com os parâmetros fornecidos e retorna um `SuccessReturn` contendo o resultado do `Datasource`
        em caso de sucesso. Se ocorrer uma exceção durante a execução do `Datasource`,
        retorna um `ErrorReturn` contendo o erro associado aos parâmetros.

        Args:
            parameters (TypeParameters): Os parâmetros a serem passados para o `Datasource`.
            datasource (Datasource[TypeDatasource, TypeParameters]): O `Datasource` a ser executado.

        Returns:
            ReturnSuccessOrError[TypeDatasource]: Um `SuccessReturn` contendo o resultado do `Datasource`
            em caso de sucesso, ou um `ErrorReturn` contendo o erro associado aos parâmetros em caso de exceção.
        """
        try:
            result = datasource(parameters)
            return SuccessReturn(result)
        except Exception:
            return ErrorReturn(parameters.error)

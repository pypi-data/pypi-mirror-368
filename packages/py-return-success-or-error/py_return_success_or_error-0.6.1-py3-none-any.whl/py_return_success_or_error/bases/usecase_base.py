"""Módulo que contém as classes base para a implementação de casos de uso.

Este módulo fornece classes abstratas que servem como base para a criação de casos de uso, seguindo
padrões de design limpo e princípios SOLID.

Classes:
    UsecaseBase: Classe base abstrata para casos de uso simples, sem acesso a fontes de dados.
UsecaseBaseCallData: Classe base abstrata para casos de uso que requerem
acesso a fontes de dados.

Tipos Genéricos:
    TypeUsecase: Tipo genérico que representa o retorno do caso de uso.

    TypeDatasource: Tipo genérico que representa a fonte de dados utilizada.

TypeParameters: Tipo genérico que representa os parâmetros de entrada,
deve herdar de ParametersReturnResult.

Este módulo também fornece funcionalidades para executar casos de uso em threads separadas
de forma transparente, além de permitir o acesso seguro a fontes de dados, tratando exceções
e retornando resultados padronizados.

Métodos:
    _resultDatasource: Usado na contrução da classe para executa operações na fonte de dados, retornando um sucesso
    com o dado esperado ou um erro predefinido.

Métodos:
    runNewThread: Executa o caso de uso em uma nova thread.

Exemplo de definição de Erros:
    >>>

        @dataclass(kw_only=True)
        class ErrorTestData(AppError):
            status_code: int
            def __str__(self) -> str:
                return f'ErrorTestData - {self.message}'

Exemplo de definição de Parâmetros:
    >>>

        @dataclass(kw_only=True)
        class PessoaParametros(ParametersReturnResult):
            nome: str
            idade: int
            error: AppError = field(default_factory=lambda: ErrorTestData(
                message='teste erro ErrorTest', status_code=400))
            def __post_init__(self):
                super().__init__(error=self.error)
            def __str__(self) -> str:
return f'TestesParametros(nome={self.nome}, idade={self.idade},
error={self.error})'

        @dataclass(kw_only=True)
        class InfoParametros(ParametersReturnResult):
            informacoes: dict

            def __str__(self) -> str:
return f'TestesParametrosGerais(informacoes={self.informacoes},
error={self.error})'

Exemplo de Uso da Classe UsecaseBase:
    >>>

        class UsecaseBaseTest(UsecaseBase[bool, InfoParametros]):
            def __call__(self, parameters: InfoParametros) -> ReturnSuccessOrError[bool]:
                if parameters.informacoes['teste'] == 'teste usecase':
                    return SuccessReturn(success=True)
                else:
                    return ErrorReturn(error=parameters.error)

        # Uso normal
        test_error = ErrorTestData(message='teste erro ErrorTest', status_code=400)
        parametros_mock = InfoParametros(
            informacoes={'teste': 'teste usecase'},
            error=test_error)
        usecase = UsecaseBaseTest()
        result = usecase(parametros_mock)

        # Uso com nova thread
        result_thread = usecase.runNewThread(parametros_mock)

        # O resultado será retornado após a conclusão da thread
        if isinstance(result, SuccessReturn):
            print(result.result)

Exemplo de Uso da Classe UsecaseBaseCallData:
    >>>

        class ExternalMock():
            def getData(self, teste_call: bool) -> bool:
                if teste_call:
                    return True
                else:
                    raise ValueError('Simulação de erro')

        class DataSourceTest(Datasource[bool, PessoaParametros]):
            def __init__(self, external_mock: ExternalMock):
                self.__external_mock = external_mock

            def __call__(self, parameters: PessoaParametros) -> bool:
                return self.__external_mock.getData(parameters.idade >= 18)

        class UsecaseBaseCallDataTest(UsecaseBaseCallData[str, bool, PessoaParametros]):
            def __call__(self, parameters: PessoaParametros) -> ReturnSuccessOrError[str]:
                # Uso do _resultDatasource para acesso seguro aos dados
                data = self._resultDatasource(parameters=parameters, datasource=self._datasource)

                if isinstance(data, SuccessReturn):
                    return SuccessReturn(success='Maior de idade')
                else:
                    return ErrorReturn(error=parameters.error)

        # Uso normal
        external_mock = ExternalMock()
        datasource_mock = DataSourceTest(external_mock)
        parametros_mock = PessoaParametros(nome='teste', idade=18)
        usecase = UsecaseBaseCallDataTest(datasource_mock)
        result = usecase(parametros_mock)

        # Uso com nova thread
        result_thread = usecase.runNewThread(parametros_mock)

        # O resultado será retornado após a conclusão da thread
        if isinstance(result, SuccessReturn):
            print(result.result)
"""
from py_return_success_or_error.imports import (
    ABC,
    Datasource,
    Generic,
    ParametersReturnResult,
    RepositoryMixin,
    ReturnSuccessOrError,
    ThreadMixin,
    TypeVar,
    abstractmethod,
)

TypeUsecase = TypeVar('TypeUsecase')
TypeDatasource = TypeVar('TypeDatasource')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class UsecaseBase(
        ABC, Generic[TypeUsecase, TypeParameters], ThreadMixin[TypeUsecase]):
    """Classe base abstrata para implementação de casos de uso simples.

    Esta classe deve ser herdada para criar casos de uso que não necessitam
    de acesso direto a fontes de dados.

    Definição de Tipos de Retorno e Parâmetros:
        Generic[TypeUsecase]: Tipo de retorno do caso de uso

        Generic[TypeParameters]: Tipo dos parâmetros de entrada
    """

    @abstractmethod
    def __call__(
            self, parameters: TypeParameters) -> ReturnSuccessOrError[TypeUsecase]:
        """Método abstrato para executar o caso de uso.

        Args:
            parameters (TypeParameters): Parâmetros necessários para execução

        Returns:
            ReturnSuccessOrError[TypeUsecase]: Resultado da execução do caso de uso
        """
        pass   # pragma: no cover


class UsecaseBaseCallData(
        ABC, Generic[TypeUsecase, TypeDatasource, TypeParameters], RepositoryMixin, ThreadMixin[TypeUsecase]):
    """Classe base abstrata para implementação de casos de uso com acesso a dados.

    Esta classe deve ser herdada para criar casos de uso que necessitam
    de acesso a fontes de dados através de um datasource.

    Attributes:
        _datasource (Datasource): Fonte de dados utilizada pelo caso de uso

    Definição de Tipos de Retorno e Parâmetros:
        Generic[TypeUsecase]: Tipo de retorno do caso de uso

        Generic[TypeDatasource]: Tipo da fonte de dados

        Generic[TypeParameters]: Tipo dos parâmetros de entrada
    """

    def __init__(
            self, datasource: Datasource[TypeDatasource, TypeParameters]) -> None:
        """Inicializa o caso de uso com uma fonte de dados.

        Args:
            datasource (Datasource[TypeDatasource, TypeParameters]):
                Fonte de dados a ser utilizada
        """
        self._datasource = datasource

    @abstractmethod
    def __call__(
            self, parameters: TypeParameters) -> ReturnSuccessOrError[TypeUsecase]:
        """Método abstrato para executar o caso de uso.

        Args:
            parameters (TypeParameters): Parâmetros necessários para execução

        Returns:
            ReturnSuccessOrError[TypeUsecase]: Resultado da execução do caso de uso
        """
        pass   # pragma: no cover

from py_return_success_or_error.imports import (
    ABC,
    Generic,
    ParametersReturnResult,
    TypeVar,
    abstractmethod,
)

TypeDatasource = TypeVar('TypeDatasource')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class Datasource(ABC, Generic[TypeDatasource, TypeParameters]):
    """Classe base abstrata para uma fonte de dados.

    Esta classe deve ser herdada por qualquer classe que implemente uma fonte de dados.
    Ela exige a implementação do método `__call__`.

    A classe Datasource padroniza a implementação de chamadas externas à aplicação,
    obrigando a pré-determinação do tipo do retorno esperado, usando a classe
    ParametersReturnResult como os parâmetros necessários para executar a chamada.

    Atributos:
        TypeDatasource: O tipo da fonte de dados.
        TypeParameters: O tipo dos parâmetros, que deve ser uma subclasse de ParametersReturnResult.
    """

    @abstractmethod
    def __call__(self, parameters: TypeParameters) -> TypeDatasource:
        """Executa a fonte de dados com os parâmetros fornecidos.

        Args:
            parameters (TypeParameters): Os parâmetros para executar a fonte de dados.

        Retorna:
            TypeDatasource: O resultado da execução da fonte de dados.

        Examples:
            >>>

                @dataclass(kw_only=True)
                class ErrorTestData(AppError):
                    status_code: int
                    def __str__(self) -> str:
                        return f'ErrorTestData - {self.message}'

                @dataclass(kw_only=True)
                class PessoaParametros(ParametersReturnResult):
                    nome: str
                    idade: int
                    error: AppError = field(default_factory=lambda: ErrorTestData(
                        message='teste erro ErrorTest', status_code=400))
                    def __post_init__(self):
                        super().__init__(error=self.error)
                    def __str__(self) -> str:
                        return f'TestesParametros(nome={self.nome}, idade={
                            self.idade}, error={self.error})'

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

                def testeDataSourceSucesso():
                    external_mock = ExternalMock()
                    datasource_test = DataSourceTest(external_mock)
                    parameters = PessoaParametros(nome='teste', idade=20)
                    result = datasource_test(parameters)
                    return result #resultado esperado é "True"
        """
        pass  # pragma: no cover

from py_return_success_or_error.imports import (
    ABC,
    Generic,
    TypeVar,
    abstractmethod,
)
from py_return_success_or_error.interfaces.app_error import AppError

TypeData = TypeVar('TypeData')


class ReturnSuccessOrError(ABC, Generic[TypeData]):
    """Classe base para manipulação de retornos de operações.

    Provê uma estrutura para representar o resultado de uma operação,
    seja ela bem-sucedida ou com erro.

    Raises:
        ValueError: Se a subclasse não for SuccessReturn ou AppError.
    """

    def __init__(self) -> None:
        if not isinstance(self, (SuccessReturn, AppError)):
            raise ValueError("SubClass Invalida.")

    @abstractmethod
    def __str__(self) -> str:
        """Retorna a representação string do resultado.

        Returns:
            str: Representação textual do sucesso ou erro.
        """


class SuccessReturn(ReturnSuccessOrError[TypeData]):
    """Representa o resultado bem-sucedido de uma operação.

    Esta classe é utilizada para encapsular o valor de retorno
    quando uma operação é concluída com sucesso.

    Attributes:
        __success (TypeData): O valor retornado pela operação bem-sucedida.

    Type Parameters:
        TypeData: O tipo do dado retornado em caso de sucesso.
    """

    def __init__(self, success: TypeData) -> None:
        """Inicializa a classe com um valor de sucesso.

        Args:
            success (TypeData): Valor de sucesso da operação.
        """
        self.__success = success

    @property
    def result(self) -> TypeData:
        if self.__success is None:
            raise ValueError("Não pode retornar um valor nulo.")
        return self.__success

    def __str__(self) -> str:
        """Retorna a representação do success."""
        return f'Success: {self.result}'


class ErrorReturn(ReturnSuccessOrError[TypeData]):
    """Classe que representa o retorno de uma operação com erro.

    Encapsula um objeto de erro (AppError) que contém os detalhes
    da falha ocorrida durante a execução de uma operação.

    Attributes:
        __error (AppError): Objeto que contém os detalhes do erro ocorrido.

    Type Parameters:
        TypeData: Tipo genérico para manter consistência com a classe base.
    """

    def __init__(self, error: AppError) -> None:
        """Inicializa uma nova instância de ErrorReturn.

        Args:
            error (AppError): Objeto de erro a ser encapsulado.
        """
        self.__error = error

    @property
    def result(self) -> AppError:
        """Retorna o objeto de erro encapsulado.

        Returns:
            AppError: O objeto de erro armazenado.

        Raises:
            ValueError: Se o erro armazenado for None.
        """
        if self.__error is None:
            raise ValueError("Não pode retornar um valor nulo.")
        return self.__error

    def __str__(self) -> str:
        """Retorna a representação textual do erro.

        Returns:
            str: String formatada contendo a mensagem de erro.
        """
        return f'Error: {self.result}'

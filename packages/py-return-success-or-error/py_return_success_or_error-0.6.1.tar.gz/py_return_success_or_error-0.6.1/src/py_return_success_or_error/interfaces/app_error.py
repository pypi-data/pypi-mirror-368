from py_return_success_or_error.imports import (
    ABC,
    abstractmethod,
    dataclass,
)


@dataclass(kw_only=True)
class AppError(ABC, Exception):
    """Data Classe base abstrata para representar erros de aplicação.

    Attributes:
        message (str): A mensagem de erro.
    """

    message: str

    @abstractmethod
    def __str__(self) -> str:
        """Retorna a representação em string do erro.

        Returns:
            str: A representação em string do erro.
        """


@dataclass
class ErrorGeneric(AppError):
    """Data Classe para representar um erro genérico.

    Methods:
        __str__: Retorna a representação em string do erro genérico.
    """

    def __str__(self) -> str:
        """Retorna a representação em string do erro genérico.

        Returns:
            str: A representação em string do erro genérico.
        """
        return f'ErrorGeneric - {self.message}'

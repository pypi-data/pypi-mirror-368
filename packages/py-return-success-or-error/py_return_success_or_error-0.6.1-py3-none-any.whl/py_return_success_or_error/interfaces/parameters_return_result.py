from py_return_success_or_error.imports import (
    ABC,
    abstractmethod,
    dataclass,
    field,
    TypeVar,

)
from py_return_success_or_error.interfaces.app_error import AppError, ErrorGeneric

TypeError = TypeVar("TypeError", bound=AppError, covariant=True)

@dataclass
class ParametersReturnResult(ABC):
    """Classe base abstrata para representar os parâmetros passados para uma função.

    Esta data class padroniza a passagem de parâmetros na aplicação, garantindo que o tipo de erro
    (AppError) seja predefinido ao chamar uma função.

    Attributes:
        error (AppError): Instância de AppError que descreve o erro ocorrido.
    """

    error: TypeError

    @abstractmethod
    def __str__(self) -> str:
        """Retorna a representação do sucesso ou erro.

        Returns:
            str: Representação textual do sucesso ou erro.
        """


@dataclass
class NoParams(ParametersReturnResult):
    """Classe que representa um resultado sem parâmetros específicos.

    Attributes:
        error (AppError): Instância de AppError que descreve o erro ocorrido.
    """

    error: AppError = field(default_factory=lambda: ErrorGeneric(message='General Error'))

    def __str__(self) -> str:
        """Retorna a representação textual do erro genérico.

        Returns:
            str: Representação textual do erro genérico.
        """
        return self.__repr__()

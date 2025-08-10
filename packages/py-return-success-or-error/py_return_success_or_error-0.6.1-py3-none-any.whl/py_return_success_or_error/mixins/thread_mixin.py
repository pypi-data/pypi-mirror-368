from py_return_success_or_error.imports import (
    Generic,
    ParametersReturnResult,
    Queue,
    ReturnSuccessOrError,
    Thread,
    TypeVar,
)

TypeUsecase = TypeVar('TypeUsecase')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class ThreadMixin(Generic[TypeUsecase]):
    """
    Mixin para fornecer funcionalidade de execução em threads.

    Esta mixin permite executar uma função em uma thread separada,
    retornando um `ReturnSuccessOrError` com o resultado da função ou um erro.


    """

    def runNewThread(
            self, parameters: TypeParameters
    ) -> ReturnSuccessOrError[TypeUsecase]:
        """
        Executa uma função em uma thread separada e retorna o resultado.

        Este método recebe uma função e um objeto de parâmetros, executa a função
        em uma thread separada e retorna um `ReturnSuccessOrError` com o resultado
        da função ou um erro, caso ocorra uma exceção.
        Args:
            function (Callable[[TypeParameters], TypeReturn]): A função a ser executada.
            parameters (TypeParameters): O objeto de parâmetros para a função.
        Returns:
            ReturnSuccessOrError[TypeReturn]: Um `ReturnSuccessOrError` contendo o resultado da função
            ou um erro, caso ocorra uma exceção.
        """
        result_queue: Queue[ReturnSuccessOrError[TypeUsecase]] = Queue()

        def targetFunction(params):
            result = self(params)
            result_queue.put(result)

        thread = Thread(target=targetFunction, args=(parameters,))
        thread.start()
        thread.join()
        result = result_queue.get()

        return result

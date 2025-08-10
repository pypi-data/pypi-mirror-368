class Empty:
    """Classe singleton para representar um valor Vazio.

    A classe Empty é usada para criar uma única instância que representa um valor vazio.
    """

    _instance = None

    def __new__(cls) -> 'Empty':
        """Cria uma nova instância da classe Empty, se ainda não existir.
        Este método garante que apenas uma instância da classe Empty seja criada (singleton).

        Returns:
            Empty: A instância única da classe Empty.
        """
        if cls._instance is None:
            cls._instance = super(Empty, cls).__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        """Retorna a representação em string da instância Empty.

        Returns:
            str: A string "Empty".
        """
        return "Empty"  # pragma: no cover


EMPTY = Empty()
"""
Uma instância única da classe Empty.

Examples:
    >>>result = EMPTY
    str(result) == "Empty"
Esta constante é usada para representar um valor vazio.
"""

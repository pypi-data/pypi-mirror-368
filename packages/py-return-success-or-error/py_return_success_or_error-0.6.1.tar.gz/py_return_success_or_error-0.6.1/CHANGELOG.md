## 0.6.1
- Correção da documentação.

## 0.6.0
- Correção do `TypeError` em `testUsecaseBaseCallDataSucesso` e `testUsecaseBaseCallDataErro` no arquivo `usecase_base_test.py` ao instanciar `PessoaParametros` e `InfoParametros` sem o argumento `error`.
- Adição de `field(default_factory=lambda: ErrorTestData(message='teste erro ErrorTest', status_code=400))` ao atributo `error` nas classes `PessoaParametros` e `InfoParametros` em `tests/helpers/auxiliares_mock.py`, tornando o argumento opcional e fornecendo um valor padrão.

## 0.5.3
1 - Correção de bug. Adicionada lista `__all__` no `__init__.py` para resolver erro do MyPy "Module does not explicitly export attribute"


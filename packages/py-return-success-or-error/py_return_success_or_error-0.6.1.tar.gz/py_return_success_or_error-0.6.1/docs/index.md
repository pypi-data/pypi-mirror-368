![logo do projeto](assets/logo.png){width="300" .center}
# py-return-success-or-error

## Visão Geral

A biblioteca `py-return-success-or-error` é uma solução robusta para tratamento de retornos e erros em aplicações Python, seguindo princípios de design limpo e arquitetura limpa.

## Principais Componentes

### 1. Tratamento de Retornos
- `ReturnSuccessOrError`: Classe base para representar retornos de operações
- `SuccessReturn`: Representa operações bem-sucedidas
- `ErrorReturn`: Representa operações com erro

### 2. Tratamento de Erros
- `AppError`: Classe base para erros de aplicação personalizados
- `ParametersReturnResult`: Padronização de parâmetros com tratamento de erros

### 3. Casos de Uso
- `UsecaseBase`: Para casos de uso simples sem acesso a fontes de dados
- `UsecaseBaseCallData`: Para casos de uso com acesso a fontes de dados externas

## Recursos Principais

- Suporte a execução de casos de uso em threads separadas
- Tratamento genérico de erros e sucessos
- Tipagem forte e segura
- Padrões de design SOLID
- Suporte a fontes de dados externas

### Principais Características

- **Tratamento Explícito de Resultados**: Fornece uma abordagem clara para lidar com sucessos e erros em operações.
- **Design Orientado a Princípios SOLID**: Utiliza classes abstratas e genéricas para criar uma estrutura flexível e extensível.
- **Segurança de Tipos**: Implementa tipagem genérica para garantir consistência nos retornos.
- **Padrão Singleton**: Utiliza técnicas como singleton para gerenciar instâncias únicas.

### Benefícios

- Reduz a complexidade do tratamento de erros
- Melhora a legibilidade do código
- Facilita a manutenção e evolução de sistemas
- Promove uma arquitetura de software mais limpa e previsível

### Casos de Uso

Ideal para projetos que necessitam de:

- Tratamento consistente de operações que podem falhar
- Arquiteturas de software com alta necessidade de tratamento de erros
- Desenvolvimento de aplicações com requisitos complexos de fluxo de execução

A biblioteca oferece uma abordagem moderna e pythônica para gerenciar retornos de operações, tornando o código mais robusto e expressivo.

# fulltrader

Pacote Python para disponibilizar dados da FullTrader. Nesta primeira versão, entregamos um "Hello World" com uma estrutura robusta, pronta para evoluir para consultas a banco de dados e APIs internas.

## Instalação (após publicar no PyPI)

```bash
pip install fulltrader
```

## Uso (API)

```python
from fulltrader import hello

print(hello())          # "Hello, FullTrader!"
print(hello("Você"))   # "Hello, Você!"
```

## Uso (CLI)

```bash
fulltrader --name "FullTrader"
```

## Desenvolvimento

Requisitos: Python 3.9+

```bash
# Instalar dependências de desenvolvimento
python -m pip install -U pip
python -m pip install -e .[dev]

# Testes
pytest

# Lint (opcional)
ruff check

# Build do pacote
python -m build
```

## Publicação

- TestPyPI (recomendado primeiro):

```bash
python -m twine upload --repository testpypi dist/*
```

- PyPI oficial:

```bash
python -m twine upload dist/*
```

Certifique-se de ter configurado `~/.pypirc` com suas credenciais.

## Estrutura

- `src/fulltrader/` código fonte (layout src)
  - `use_cases/` casos de uso (ex.: `hello`)
  - `core/shared/` utilitários e contratos compartilhados
  - `infra/` camadas de integração (DB, APIs) – a serem implementadas
  - `cli.py` ponto de entrada da linha de comando
- `tests/` testes unitários

Licença: MIT

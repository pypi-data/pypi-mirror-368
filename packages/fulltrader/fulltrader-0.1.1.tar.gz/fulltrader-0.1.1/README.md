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
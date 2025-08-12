# AliasAnx

Biblioteca para gerar arquivos ANX (Alias) em Python.

## Instalação

pip install AliasAnx

## Uso rápido

```python
from aliasanx import Pyanx

px = Pyanx()

px.add_node(entity_type='Person', label='Alice', ring_color=255, description='Pessoa exemplo')
px.add_node(entity_type='Person', label='Bob')
px.add_edge('Alice', 'Bob', label='knows', color=0, style='Solid')

px.create('exemplo.anx')
```

## Licença

Apache-2.0

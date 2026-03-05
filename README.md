# SpaceX ETL Pipeline

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![SQLite](https://img.shields.io/badge/database-SQLite-green.svg)
![Pandas](https://img.shields.io/badge/library-Pandas-orange.svg)
Uma solução modular e reutilizável para extração, transformação e carregamento (ETL) de dados da API SpaceX para um banco de dados SQLite.


## Visão Geral

Este projeto implementa um pipeline ETL genérico que pode ser adaptado para qualquer fonte de dados em API REST. A arquitetura foi desenvolvida seguindo padrões de engenharia de software que permitem fácil manutenção, extensão e reutilização em projetos futuros.

## Arquitetura

O projeto segue uma arquitetura em camadas com separação clara de responsabilidades:

- **Extract (extract.py)**: Responsável por conectar à API e extrair dados
- **Transform (transform.py)**: Normaliza e estrutura os dados
- **Load (load.py)**: Persiste os dados em banco de dados
- **Pipeline (pipeline.py)**: Orquestra o fluxo ETL completo
- **Main (main.py)**: Ponto de entrada da aplicação

## Características

- Extração de dados diretamente da API sem arquivos intermediários
- Processamento eficiente usando geradores (yield) para economizar memória
- Normalização automática de estruturas de dados aninhadas
- Suporte para autenticação por API key
- Transformações customizadas por endpoint
- Banco de dados SQLite com schema automático
- Logging detalhado para debugging
- Código totalmente tipado com type hints

## Instalação

### Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Dependências

```bash
pip install requests pandas sqlalchemy
```

## Uso

### Execução Básica

```bash
python main.py
```

### Uso como Biblioteca

```python
from pipeline import ETLPipeline

# Criar instância do pipeline
pipeline = ETLPipeline(
    api_url='https://api.spacexdata.com/v3/',
    db_path='space_data.db'
)

# Executar para múltiplos endpoints
endpoints = {
    'rockets': 'rockets',
    'launchpads': 'launchpads',
    'ships': 'ships'
}

results = pipeline.run(endpoints)
pipeline.close()
```

### Transformações Customizadas

```python
def custom_transform(records_gen):
    for record in records_gen:
        record['processed_date'] = '2026-03-05'
        yield record

pipeline.register_transformation('rockets', custom_transform)
```

### Consultas ao Banco de Dados

```python
# Query SQL direta
df = pipeline.loader.query("SELECT * FROM rockets LIMIT 5")
print(df)

# Informações de esquema
schema = pipeline.loader.get_table_info('rockets')
print(schema)
```

## Estrutura de Arquivos

```
SpaceX-etl/
├── Etl pipeline/
│   ├── extract.py       # Extrator genérico de APIs
│   ├── transform.py     # Transformador de dados
│   ├── load.py          # Loader para SQLite
│   ├── pipeline.py      # Orquestrador ETL
│   ├── main.py          # Ponto de entrada
│   └── __pycache__/     # Cache Python
├── README.md            # Este arquivo
└── spacex.db            # Banco de dados (gerado)
```

## Componentes

### APIExtractor

Responsável por conectar e extrair dados de APIs REST.

**Métodos principais:**
- `fetch(endpoint)`: Extrai dados de um endpoint e retorna um gerador

```python
from extract import APIExtractor

extractor = APIExtractor('https://api.spacexdata.com/v3/')
for record in extractor.fetch('rockets'):
    print(record)
```

### DataTransformer

Normaliza estruturas de dados aninhadas em DataFrames planos.

**Métodos principais:**
- `to_dataframe(selected_columns, flatten)`: Converte registros em DataFrame
- `apply_transformation(func)`: Aplica função customizada aos registros

**Funcionalidades:**
- Flattening automático de dicionários aninhados
- Conversão de listas para JSON strings
- Seleção de colunas específicas

```python
from transform import DataTransformer

transformer = DataTransformer(records_generator)
df = transformer.to_dataframe(flatten=True)
```

### DatabaseLoader

Gerencia persistência de dados em SQLite com tratamento de erros.

**Métodos principais:**
- `save(df, table_name)`: Salva DataFrame como tabela
- `query(sql)`: Executa queries SQL
- `get_table_info(table_name)`: Retorna esquema da tabela

```python
from load import DatabaseLoader

loader = DatabaseLoader('dados.db')
loader.save(dataframe, 'minha_tabela')
df_resultado = loader.query("SELECT * FROM minha_tabela")
```

### ETLPipeline

Orquestrador que coordena todo o fluxo de extração, transformação e carregamento.

**Métodos principais:**
- `process_endpoint(endpoint, table_name)`: Processa um endpoint completo
- `run(endpoints)`: Executa pipeline para múltiplos endpoints
- `register_transformation(endpoint, func)`: Registra transformação customizada

## Exemplo de Saída

Ao executar o pipeline, você verá:

```
==================================================
Processing: landpads
==================================================
Records: 5
Columns: ['id', 'name', 'region', 'latitude', 'longitude', ...]
   id          name           region   latitude  longitude
0  123  Port Canaveral     Florida    28.4104   -80.6188
1  124  Port of LA   California    33.7427   -118.2426
...
Loading 5 records into 'landpads'
✓ Loaded 5 records into 'landpads'
```

## Tratamento de Dados

### Normalização de Estruturas Aninhadas

Dados aninhados são automaticamente normalizados:

**Entrada:**
```json
{
  "name": "Port Canaveral",
  "location": {
    "region": "Florida",
    "coordinates": {
      "latitude": 28.4104,
      "longitude": -80.6188
    }
  }
}
```

**Saída no banco de dados:**
```
name: "Port Canaveral"
location_region: "Florida"
location_coordinates_latitude: 28.4104
location_coordinates_longitude: -80.6188
```

## Tratamento de Erros

O pipeline implementa tratamento robusto de erros:

- Erros de conexão à API são capturados e relatados
- Dados ausentes são ignorados com mensagens de aviso
- Erros de persistência exibem detalhes completos
- Stack traces detalhados para debugging

## Otimizações

### Uso de Geradores

Todos os componentes utilizam geradores para economizar memória:

```python
def fetch(self, endpoint: str) -> Generator[dict, None, None]:
    # Retorna um gerador em vez de lista completa
    for record in response.json():
        yield record
```

### Processamento em Stream

Dados fluem diretamente da API para o banco sem intermediários:

API -> Extract (yield) -> Transform (yield) -> Load

## Extensibilidade

### Adicionar Novo Extrator

```python
class GraphQLExtractor(APIExtractor):
    def fetch(self, query: str):
        # Implementar lógica GraphQL
        pass
```

### Adicionar Novo Loader

```python
class PostgreSQLLoader(DatabaseLoader):
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
```

### Transformações Customizadas

```python
def cleanup_rockets(records):
    for record in records:
        record['name'] = record['name'].upper()
        record['active_years'] = str(record['active'])
        yield record

pipeline.register_transformation('rockets', cleanup_rockets)
```

## Requisitos de Projeto

Este projeto foi desenvolvido com foco em:

- Modularidade: Componentes independentes e reutilizáveis
- Escalabilidade: Suporta grandes volumes de dados
- Manutenibilidade: Código limpo e bem documentado
- Testabilidade: Cada componente pode ser testado isoladamente
- Documentação: Type hints e docstrings completos
- Padrões: Segue boas práticas de engenharia de software

## Casos de Uso

- Ingestão de dados de APIs REST genéricas
- Pipeline de dados para data warehousing
- ETL em projetos analytics e business intelligence
- Integração de múltiplas fontes de dados
- Sincronização periódica de dados

## Limitações Atuais

- Suporta apenas SQLite (extensível para outros bancos)
- Não implementa retry automático em falhas de rede
- Sem suporte para paginação automática (manual via API)
- Sem agendamento de execução (requer orquestrador externo)

## Roadmap Futuro

- Suporte para múltiplos bancos de dados (PostgreSQL, MySQL)
- Sistema de cache para evitar reexecuções
- Validação de esquema de dados
- Testes unitários automatizados
- CLI com argumentos de configuração
- Suporte para dados em formato Parquet
- Logging estruturado

## Contribuindo

Para utilizar este projeto em futuros desenvolvimentos:

1. Clone o repositório
2. Instale as dependências
3. Adapte os endpoints conforme necessário
4. Implemente transformações customizadas para seus dados
5. Configure o banco de dados desejado

## Licença

Este projeto é de código aberto e disponível para uso educacional e comercial.

---

Última atualização: Março 2026

# 🐍 SnakeStack

![Python](https://img.shields.io/badge/python-^3.13-blue)
![Poetry](https://img.shields.io/badge/poetry-2.1.3+-blueviolet)
![Pipeline](https://github.com/BrunoSegato/snakestack/actions/workflows/ci.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/snakestack.svg)](https://pypi.org/project/snakestack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📦 Visão Geral

O `snakestack` é um pacote modular que oferece uma base robusta para construção de serviços backend com foco em:

- Observabilidade com OpenTelemetry
- Cache assíncrono com Redis
- Integração com Google Pub/Sub
- Acesso assíncrono ao MongoDB
- Client HTTPX com suporte a tracing
- Modelos base com `pydantic` e `pydantic-settings`
- Stack de logging estruturado e configurável

---

## ⚙️ Instalação

### Instalação base:

#### Via PIP

```bash
pip install snakestack
```

#### Via Poetry

```bash
poetry add snakestack
```

### Extras disponíveis:

| Extra     | Comando de instalação               |
| --------- | ----------------------------------- |
| Redis     | `pip install snakestack[redis]`     |
| MongoDB   | `pip install snakestack[mongodb]`   |
| Pub/Sub   | `pip install snakestack[pubsub]`    |
| Telemetry | `pip install snakestack[telemetry]` |
| Todos     | `pip install snakestack[all]`       |

---

## 🧪 Testes

O projeto possui cobertura completa de testes unitários e está organizado por domínios.

### Executar todos os testes:

```bash
make test
```

### Rodar testes com cobertura:

```bash
make test-ci
```

### Rodar testes de um domínio específico:

```bash
pytest -m cache
pytest -m pubsub
pytest -m telemetry
```

---

## 🛠️ Desenvolvimento Local

### 1. Clone o repositório:

```bash
git clone https://github.com/BrunoSegato/snakestack.git
cd snakestack
```

### 2. Instale as dependências:

```bash
make install
```

### 3. Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

---

## 🧾 Comandos Úteis

| Comando          | Descrição                               |
| ---------------- | --------------------------------------- |
| `make install`   | Instala dependências com Poetry         |
| `make check`     | Executa linters e mypy                  |
| `make lint`      | Roda `ruff` com auto-fix                |
| `make test`      | Executa os testes unitários             |
| `make cov`       | Gera relatório de cobertura             |
| `make changelog` | Gera changelog com Towncrier            |
| `make bump`      | Realiza bump de versão com Commitizen   |
| `make release`   | Gera changelog, bump e cria release/tag |

---

## 📚 Módulos disponíveis

* `snakestack.logging`: Configuração de log estruturado com filtros e formatadores.

* `snakestack.cache`: Cliente Redis assíncrono com decorator de cache.

* `snakestack.pubsub`: Publisher e subscriber com suporte a presets, tracing e decorators.

* `snakestack.telemetry`: Integração com OpenTelemetry (métricas, traces e logging).

* `snakestack.mongodb`: Client assíncrono para MongoDB com tracing integrado.

* `snakestack.healthz`: Health check para status da aplicação e dependências.

* `snakestack.httpx`: Client HTTPX instrumentado.

* `snakestack.model`: Base de modelos pydantic para uso interno.

* `snakestack.config`: Gerenciamento de settings com pydantic-settings.

---

## 🧪 Exemplos de Uso
🚧 Em construção — em breve serão adicionados exemplos práticos de uso para cada módulo.

### Módulo Cache

#### Código

```python
async def sample():
    client = create_async_redis_client()
    redis = AsyncRedisService(client, default_ttl=3600)

    values = [
        "foo",
        1,
        (1, 2, 3),
        {1, 2, 3},
        datetime.now(),
        Decimal("10.50")
    ]

    for value in values:
        await redis.set("foo", value)
        print("Resultado", await redis.get("foo"))

```

#### Saída

```text
Resultado foo
Resultado 1
Resultado [1, 2, 3]
Resultado ['1', '2', '3']
Resultado 2025-08-07T18:37:02.149923
Resultado 10.50
```

---

### Módulo Healthz

#### Código

```python
async def check_async():
    await asyncio.sleep(1)
    return True

def check_sync():
    time.sleep(1)
    return True

def main():
    health_check = SnakeHealthCheck(
        service_name="Teste",
        service_version="0.0.1",
        service_environment="test"
    )
    health_check.add_check(name="check_async", func=check_async)
    health_check.add_check(name="check_sync", func=check_sync)

    result, check = asyncio.run(health_check.is_healthy())
    print(orjson.dumps(result, option=orjson.OPT_INDENT_2).decode())
```

#### Saída

```json
{
  "service_name": "Teste",
  "version": "0.0.1",
  "host": "hostname",
  "uptime": "9h 48m 24s",
  "timestamp": "2025-08-07T21:41:38.071402+00:00",
  "environment": "test",
  "status": true,
  "latency_ms": 2001.57,
  "details": {
    "check_async": {
      "ok": true,
      "latency_ms": 1001.3
    },
    "check_sync": {
      "ok": true,
      "latency_ms": 1000.27
    }
  }
}
```

---

### Módulo Httpx

#### Código

```python
class MyAPI(SnakeHttpClient):

    async def get_user(
        self,
    ):
        response = await self.handle(
            method="GET",
            url="/get"
        )
        response.raise_for_status()
        return response.json()


async def without_context():
    api = MyAPI(base_url="https://httpbin.org")
    try:
        result = await api.get_user()
        print(orjson.dumps(result, option=orjson.OPT_INDENT_2).decode())
    finally:
        await api.aclose()


async def with_context():
    async with MyAPI(base_url="https://httpbin.org") as api:
        result = await api.get_user()
        print(orjson.dumps(result, option=orjson.OPT_INDENT_2).decode())
```

#### Saída

```json
{
  "args": {},
  "headers": {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Host": "httpbin.org",
    "User-Agent": "python-httpx/0.28.1",
    "X-Amzn-Trace-Id": "Root=1-68951eda-3b5b8fea7c3dfa3a11b7aac3"
  },
  "origin": "127.0.0.1",
  "url": "https://httpbin.org/get"
}
{
  "args": {},
  "headers": {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Host": "httpbin.org",
    "User-Agent": "python-httpx/0.28.1",
    "X-Amzn-Trace-Id": "Root=1-68951edb-20f0559d24678dd873b96338"
  },
  "origin": "127.0.0.1",
  "url": "https://httpbin.org/get"
}

```

---

### Módulo Logging

#### 1. Exemplo com formatter `default`

##### Código

```python
def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Logging simples funcionando.")
```

##### Saída

```text
2025-08-07 18:50:14,385 [INFO] __main__: Logging simples funcionando.
```

#### 2. Exemplo com formatter `with_request_id`

##### Variável de ambiente

```bash
SNAKESTACK_LOG_DEFAULT_FORMATTER=with_request_id
```

##### Código

```python
def main():
    set_request_id("12345678")
    logger.info("Logging with_request_id funcionando.")


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    main()
```

##### Saída

```text
2025-08-08 16:44:43,236 [INFO] [req_id=12345678] __main__: Logging with_request_id funcionando.
```

#### 3. Exemplo com formatter `custom_json`

##### Variável de ambiente

```bash
SNAKESTACK_LOG_DEFAULT_FORMATTER=custom_json
```

##### Código

```python
def main():
    set_request_id("12345678")
    logger.info("Logging custom_json funcionando.")


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    main()
```

##### Saída

```json
{"time":"2025-08-08T19:47:53.572825+00:00","level":"INFO","pid":175425,"name":"__main__:8","msg":"Logging with_request_id funcionando.","request":{"id":"12345678"}}
```

#### 4. Exemplo com filter `excluded_name`

##### Variável de ambiente

```bash
SNAKESTACK_LOG_DEFAULT_FILTERS=excluded_name,request_id
SNAKESTACK_LOG_DEFAULT_FORMATTER=with_request_id
SNAKESTACK_LOG_EXCLUDED_NAME=ignore.me
```

##### Código

```python
def main():
    set_request_id("12345678")
    logger.info("Logging com filtro excluded_name funcionando.")
    logger_exclude.info("Logging será descartado pelo filtro.")


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger_exclude = logging.getLogger("exclude.me")
    main()
```

##### Saída

```text
2025-08-08 16:58:29,570 [INFO] [req_id=12345678] __main__: Logging com filtro excluded_name funcionando.
```

---

## 🧭 Roadmap

* [x] Modularização por domínio

* [x] Cobertura completa de testes unitários

* [x] Suporte a extras no PyPI

* [ ] Documentação online (mkdocs)

* [ ] Dashboard de observabilidade com Tempo + Prometheus + Grafana

* [ ] CI/CD com deploy automático no PyPI

* [ ] CLI para validação de ambientes e testes locais

* [ ] Criação de CHANGELOG via towncrier

---

## 👨‍💻 Autor

Desenvolvido por [`Bruno Segato`](mailto:brunosegatoit@gmail.com) — contribuições, sugestões e feedbacks são sempre bem-vindos!

---

## 📝 Licença

Este projeto está licenciado sob os termos da **MIT License**.

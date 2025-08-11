# AppServer SDK Python AI

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

SDK Python para integração com serviços de IA da AppServer.

## 🚀 Características

- Cliente HTTP assíncrono e síncrono
- Modelos Pydantic para validação de dados
- Retry automático com backoff exponencial  
- Type hints completos
- Suporte a múltiplos provedores de IA
- Logging estruturado
- Testes abrangentes

## 📦 Módulos Disponíveis

### 🤖 LLM (Large Language Models)
Módulo profissional para integração com modelos de linguagem e APIs de inteligência artificial.

**Características principais:**
- Cliente assíncrono e síncrono
- Retry automático com backoff exponencial
- Suporte a múltiplos provedores de IA
- Modelos Pydantic com type hints completos
- Sistema de logging estruturado
- Gerenciamento seguro de API keys

📖 **[Documentação completa do LLM](docs/llm.md)**

### 🔍 WebScraping
Módulo profissional de web scraping com conversão para markdown usando Docling.

**Características principais:**
- Scraping robusto com retry automático
- Conversão de alta qualidade usando Docling (IBM)
- Processamento paralelo de múltiplas URLs
- Sistema de cache inteligente
- Limpeza automática de conteúdo
- Extração de metadados ricos

📖 **[Documentação completa do WebScraping](docs/webscraping.md)**

## 📦 Instalação

### Via Poetry (Recomendado)
```bash
poetry add appserver-sdk-python-ai
```

### Via pip
```bash
pip install appserver-sdk-python-ai
```

### Via GitHub (Desenvolvimento)
```bash
# Via Poetry
poetry add git+https://github.com/appserver/appserver-sdk-python-ai.git

# Via pip
pip install git+https://github.com/appserver/appserver-sdk-python-ai.git
```

## 🔧 Uso Básico

### Módulo WebScraping

```python
from appserver_sdk_python_ai.webscraping import quick_scrape

# Scraping simples
markdown = quick_scrape("https://example.com")
print(markdown)
```

### Módulo LLM - Cliente Síncrono

```python
from appserver_sdk_python_ai import AIClient
from appserver_sdk_python_ai.models import AIRequest

# Configurar cliente
client = AIClient(
    base_url="https://api.appserver.com.br/ai/v1",
    api_key="sua-api-key"
)

# Fazer requisição
request = AIRequest(
    prompt="Explique machine learning em termos simples",
    model="gpt-4",
    max_tokens=500
)

response = client.chat_completion(request)
print(response.content)
```

### Módulo LLM - Cliente Assíncrono

```python
import asyncio
from appserver_sdk_python_ai import AsyncAIClient

async def main():
    client = AsyncAIClient(
        base_url="https://api.appserver.com.br/ai/v1",
        api_key="sua-api-key"
    )
    
    request = AIRequest(
        prompt="O que é inteligência artificial?",
        model="gpt-3.5-turbo"
    )
    
    response = await client.chat_completion(request)
    print(response.content)
    
    await client.close()

asyncio.run(main())
```

### Módulo LLM - Configuração Avançada

```python
from appserver_sdk_python_ai import AIClient, AIConfig

config = AIConfig(
    base_url="https://api.appserver.com.br/ai/v1",
    api_key="sua-api-key",
    timeout=30,
    max_retries=3,
    retry_delay=1.0,
    debug=True
)

client = AIClient(config=config)
```

## 🛠️ Desenvolvimento

### Pré-requisitos

- Python 3.11+
- Poetry

### Configuração do Ambiente

```bash
# Clonar repositório
git clone https://github.com/appserver/appserver-sdk-python-ai.git
cd appserver-sdk-python-ai

# Instalar dependências
poetry install

# Configurar pre-commit hooks
poetry run pre-commit install

# Ativar ambiente virtual
poetry shell
```

### Executar Testes

```bash
# Todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov=appserver_sdk_python_ai --cov-report=html

# Apenas testes unitários
poetry run pytest -m unit

# Apenas testes de integração
poetry run pytest -m integration
```

### Linting e Formatação

```bash
# Verificar e corrigir código
poetry run ruff check . --fix
poetry run ruff format .

# Verificar tipos
poetry run mypy src/

# Verificar segurança
poetry run bandit -r src/
poetry run safety check
```

### Executar Exemplo

```bash
# Exemplo básico
poetry run python examples/basic_usage.py

# Exemplo assíncrono
poetry run python examples/async_usage.py
```

## 📚 Documentação

### Documentação dos Módulos

- **[LLM](docs/llm.md)** - Guia completo do módulo de modelos de linguagem
- **[WebScraping](docs/webscraping.md)** - Guia completo do módulo de web scraping

### Estrutura do Projeto

```
appserver-sdk-python-ai/
├── src/
│   └── appserver_sdk_python_ai/
│       ├── __init__.py
│       ├── llm/                    # Módulo LLM
│       │   ├── __init__.py
│       │   ├── client/
│       │   ├── models/
│       │   └── utils/
│       ├── webscraping/            # Módulo WebScraping
│       │   ├── __init__.py
│       │   ├── core/
│       │   ├── docling/
│       │   ├── utils/
│       │   └── tests/
│       └── shared/                 # Utilitários compartilhados
│           ├── __init__.py
│           └── exceptions.py
├── tests/
├── docs/
│   └── webscraping.md             # Documentação do WebScraping
├── scripts/
└── pyproject.toml
```

### Modelos Disponíveis

- `AIRequest`: Modelo de requisição
- `AIResponse`: Modelo de resposta
- `AIConfig`: Configuração do cliente
- `AIError`: Modelo de erro

### Exceções

- `AIException`: Exceção base
- `AIConnectionError`: Erro de conexão
- `AIAuthenticationError`: Erro de autenticação
- `AIRateLimitError`: Erro de limite de taxa
- `AITimeoutError`: Erro de timeout

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Padrões de Commit

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` mudanças na documentação
- `style:` formatação de código
- `refactor:` refatoração de código
- `test:` adição ou correção de testes
- `chore:` tarefas de manutenção

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Email**: suporte@appserver.com.br
- **Issues**: [GitHub Issues](https://github.com/appserver/appserver-sdk-python-ai/issues)
- **Documentação**: [Wiki](https://github.com/appserver/appserver-sdk-python-ai/wiki)

## 📊 Status do Projeto

- ✅ Cliente básico implementado
- ✅ Modelos Pydantic
- ✅ Testes unitários
- 🔄 Documentação (em andamento)
- 🔄 Testes de integração (em andamento)
- ⏳ Suporte a streaming (planejado)
- ⏳ Cache de respostas (planejado)

---

**Desenvolvido com ❤️ pela equipe AppServer**

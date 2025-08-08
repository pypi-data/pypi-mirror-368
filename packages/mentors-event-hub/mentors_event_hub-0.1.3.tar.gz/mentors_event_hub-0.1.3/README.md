# Mentors Event Hub

![Pipeline](https://github.com/Mentorstec/mentors-event-hub/actions/workflows/pipeline.yml/badge.svg)
![PyPI Version](https://img.shields.io/pypi/v/mentors-event-hub?color=blue&logo=pypi&logoColor=white)
![Python Versions](https://img.shields.io/pypi/pyversions/mentors-event-hub?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/Mentorstec/mentors-event-hub?color=green)
![Downloads](https://img.shields.io/pypi/dm/mentors-event-hub?color=orange&logo=pypi)

Sistema centralizado de logging de eventos e exceções com suporte para Azure Service Bus.

## 🚀 Instalação

### PyPI (Público)
```bash
pip install mentors-event-hub
```

### Desenvolvimento
```bash
git clone https://github.com/mentorstec/mentors-event-hub.git
cd mentors-event-hub
pip install -e ".[dev]"
```

## 📋 Configuração

Defina as variáveis de ambiente:

```bash
export AZURE_SERVICE_BUS_CONNECTION_STRING="Endpoint=sb://..."
export AZURE_SERVICE_BUS_QUEUE_NAME="events"  # opcional, default: "events"
```

## 🎯 Uso Rápido

### Client Direto (Recomendado)

```python
from mentors_event_hub import EventHubClient

# Criar client
client = EventHubClient.create_azure_client("meu-projeto", layer="web")

# Enviar evento
client.send_event(
    event_type="USER_LOGIN",
    message="Usuário fez login",
    object="auth_service",
    tags=["auth", "success"],
    user_id=123
)

# Capturar erros automaticamente
@client.capture_errors("payment_process")
def process_payment(amount):
    if amount <= 0:
        raise ValueError("Invalid amount")
    return {"status": "success"}
```

### Funções Globais (Simples)

```python
from mentors_event_hub import setup_global_hub, send_event, capture_errors

# Configurar uma vez
setup_global_hub("meu-projeto", layer="api")

# Usar em qualquer lugar
send_event(event_type="INFO", message="Sistema iniciado")

@capture_errors("critical_function")
def my_function():
    # Erros são capturados automaticamente
    raise Exception("Something went wrong")
```

## 📊 Estrutura do Payload

Todos os eventos seguem esta estrutura:

```json
{
    "project": "meu-projeto",
    "layer": "web",
    "message": "Usuário fez login",
    "obs": "",
    "timestamp": "2025-01-07T10:30:45.123456Z",
    "event_type": "USER_LOGIN", 
    "object": "auth_service",
    "tags": ["auth", "success"]
}
```

## 🏗️ Arquitetura

O sistema usa o **Repository Pattern** para máxima flexibilidade:

```
├── EventRepository (Interface)
├── AzureServiceBusRepository (Implementação)  
├── EventHubClient (Factory + API)
└── Funções Globais (Compatibilidade)
```

### Adicionando Novos Provedores

```python
from mentors_event_hub.repository.event_repository import EventRepository

class CustomRepository(EventRepository):
    def event_handler(self, **kwargs):
        payload = self.build_payload(**kwargs)
        # Sua implementação aqui
        self.send_to_custom_service(payload)
```

## 🧪 Testes

```bash
# Executar testes
pytest tests/ -v --cov=mentors_event_hub

# Lint
black mentors_event_hub/
flake8 mentors_event_hub/
mypy mentors_event_hub/
```

## 🚀 Deploy

### Desenvolvimento
```bash
# Instalar dependências de desenvolvimento
make dev-install

# Executar testes
make test

# Linting e formatação
make lint
make format

# Build local
make build
```

### Release para PyPI

**Configuração (uma vez):**
```bash
# Configure seu token do PyPI
export PYPI_TOKEN=pypi-AgE...seu-token-aqui

# Para TestPyPI (opcional)
export PYPI_TEST_TOKEN=pypi-AgE...seu-token-testpypi-aqui
```

**Release automático:**
```bash
# Release completo (testes + build + upload)
make release

# Para TestPyPI primeiro (recomendado)
make release-test
```

**Upload manual:**
```bash
# Apenas upload (se o build já foi feito)
make upload        # PyPI
make upload-test   # TestPyPI
```

## 📝 Exemplos Avançados

### Contexto Customizado
```python
client.send_event(
    event_type="BUSINESS_ERROR",
    message="Pedido inválido",
    obs="Cliente tentou criar pedido sem itens",
    object="order_service",
    tags=["validation", "business"],
    order_id="12345",
    customer_id="67890"
)
```

### Handler de Erros Global
```python
import sys
from mentors_event_hub import EventHubClient

client = EventHubClient.create_azure_client("meu-app", "global")

def global_exception_handler(exc_type, exc_value, exc_traceback):
    import traceback
    client.send_event(
        event_type="CRITICAL_ERROR",
        message=str(exc_value),
        obs="".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
        object="uncaught_exception",
        tags=["critical", exc_type.__name__]
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler
```

## 🔧 Configurações Avançadas

### Client Customizado
```python
client = EventHubClient.create_azure_client(
    project="meu-projeto",
    layer="service", 
    connection_string="sua-connection-string",
    queue_name="eventos-customizados"
)
```

### Environment Variables
- `AZURE_SERVICE_BUS_CONNECTION_STRING` - String de conexão (obrigatória)
- `AZURE_SERVICE_BUS_QUEUE_NAME` - Nome da fila (opcional, default: "events")

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📞 Suporte

- **Email**: diego@mentorstec.com.br
- **Issues**: [GitHub Issues](https://github.com/mentorstec/mentors-event-hub/issues)

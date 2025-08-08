"""
Exemplo de uso do Event Hub com Repository Pattern
"""

from mentors_event_hub import EventHubClient, setup_global_hub, send_event, send_error, capture_errors


# === OPÇÃO 1: Client próprio (mais flexível) ===
client = EventHubClient.create_azure_client("meu-projeto", layer="web")

# Enviar evento customizado
client.send_event(
    event_type="USER_LOGIN", 
    message="Usuário fez login",
    object="auth_service",
    tags=["authentication", "success"],
    user_id=123,
    ip="192.168.1.1"
)

# Enviar erro manualmente
try:
    1 / 0
except Exception as e:
    client.send_error(e, context="divisao_por_zero", user_id=123)

# Decorator para capturar erros
@client.capture_errors("operacao_critica")
def operacao_perigosa():
    raise ValueError("Algo deu errado!")


# === OPÇÃO 2: Instance global (mais simples) ===
setup_global_hub("meu-projeto", layer="api")

# Enviar eventos direto
send_event(
    event_type="PROCESS_START", 
    message="Sistema iniciado",
    object="main_process",
    tags=["startup"]
)

# Decorator global
@capture_errors("funcao_importante")
def minha_funcao():
    raise Exception("Erro!")

# Erro manual
try:
    minha_funcao()
except:
    pass

print("Eventos enviados!")
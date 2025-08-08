# 🧪 Guia de Testes e Qualidade de Código

Este documento fornece instruções completas para executar todos os testes de qualidade e validações que são executadas na pipeline de CI/CD.

## 📋 Pré-requisitos

### Instalação das Ferramentas

```bash
# Instalar todas as dependências de desenvolvimento
pip install -e ".[dev]"

# OU instalar ferramentas individualmente
pip install black ruff mypy pytest pytest-cov
```

### Estrutura do Projeto
```
mentors_event_hub/
├── core/                    # Código fonte
│   ├── __init__.py
│   ├── event_hub.py
│   ├── event_hub_client.py
│   ├── azure/
│   └── repository/
├── tests/                   # Testes
├── pyproject.toml          # Configurações
└── docs/
```

## 🎯 Bateria Completa de Testes

### Script Automatizado

**Criar arquivo `run_tests.sh`:**
```bash
#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para prints coloridos
print_step() { echo -e "${BLUE}🔍 $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Contador de falhas
FAILURES=0

echo "🚀 Iniciando bateria completa de testes e qualidade"
echo "================================================="

# 1. FORMATAÇÃO COM BLACK
print_step "1. Verificando formatação do código com Black"
if python -m black --check core/; then
    print_success "Black: Formatação correta"
else
    print_error "Black: Código precisa ser formatado"
    echo "💡 Execute: python -m black core/"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 2. QUALIDADE COM RUFF
print_step "2. Analisando qualidade do código com Ruff"
if python -m ruff check core/; then
    print_success "Ruff: Qualidade do código OK"
else
    print_error "Ruff: Problemas de qualidade encontrados"
    echo "💡 Execute: python -m ruff check --fix core/"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 3. TIPOS COM MYPY
print_step "3. Verificando anotações de tipo com MyPy"
if python -m mypy core/ --ignore-missing-imports; then
    print_success "MyPy: Tipos corretos"
else
    print_warning "MyPy: Alguns tipos podem estar faltando (não crítico)"
fi
echo ""

# 4. TESTES COM PYTEST
print_step "4. Executando testes com PyTest"
if python -m pytest tests/ -v --cov=core --cov-report=term --cov-report=html; then
    print_success "PyTest: Todos os testes passaram"
else
    print_error "PyTest: Alguns testes falharam"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 5. VERIFICAÇÃO DE IMPORTS
print_step "5. Verificando se imports estão funcionando"
if python -c "import core; print('✅ Imports OK')"; then
    print_success "Imports: Funcionando corretamente"
else
    print_error "Imports: Problemas encontrados"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# RESUMO FINAL
echo "================================================="
if [ $FAILURES -eq 0 ]; then
    print_success "🎉 TODOS OS TESTES PASSARAM!"
    echo "✅ Código pronto para produção"
    exit 0
else
    print_error "❌ $FAILURES teste(s) falharam"
    echo "🔧 Corrija os problemas acima antes do deploy"
    exit 1
fi
```

**Uso:**
```bash
# Tornar executável e executar
chmod +x run_tests.sh
./run_tests.sh
```

## 🔧 Comandos Individuais

### 1. 🎨 Formatação (Black)

**Verificar formatação:**
```bash
python -m black --check core/
```

**Formatar código:**
```bash
python -m black core/
```

**Configuração no `pyproject.toml`:**
```toml
[tool.black]
line-length = 88
target-version = ["py38"]
include = '\.pyi?$'
```

### 2. 🔍 Qualidade (Ruff)

**Verificar qualidade:**
```bash
python -m ruff check core/
```

**Corrigir automaticamente:**
```bash
python -m ruff check --fix core/
```

**Configuração no `pyproject.toml`:**
```toml
[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]
```

### 3. 🏷️ Tipos (MyPy)

**Verificar tipos:**
```bash
python -m mypy core/ --ignore-missing-imports
```

**Verificação rigorosa:**
```bash
python -m mypy core/ --strict
```

**Configuração no `pyproject.toml`:**
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
```

### 4. 🧪 Testes (Pytest)

**Executar todos os testes:**
```bash
python -m pytest tests/ -v
```

**Com cobertura:**
```bash
python -m pytest tests/ -v --cov=core --cov-report=term
```

**Com relatório HTML:**
```bash
python -m pytest tests/ -v --cov=core --cov-report=html
# Ver relatório em htmlcov/index.html
```

**Configuração no `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
```

## 📊 Interpretação dos Resultados

### ✅ **Sucesso - Pipeline Passará**
- **Black**: `All done! ✨ 🍰 ✨`
- **Ruff**: `All checks passed!`
- **MyPy**: `Success: no issues found`
- **Pytest**: `X passed, 0 failed`

### ❌ **Falha - Pipeline Falhará**
- **Black**: `X files would be reformatted`
- **Ruff**: `Found X errors`
- **MyPy**: `Found X errors`
- **Pytest**: `X failed, Y passed`

### ⚠️ **Avisos - Pipeline Pode Passar**
- **MyPy**: Avisos sobre tipos faltantes (configurável)
- **Pytest**: Baixa cobertura (não bloqueia por padrão)

## 🚀 Integração com CI/CD

### GitHub Actions - Pipeline Equivalente

```yaml
# Mesmo comportamento da pipeline
- name: 🎨 Verificar formatação
  run: |
    echo "🎨 Verificando formatação..."
    black --check core/ || (echo "❌ Execute: black core/" && exit 1)

- name: 🔍 Análise de código
  run: |
    echo "🔍 Analisando código..."
    ruff check core/

- name: 🏷️ Verificação de tipos
  run: |
    echo "🏷️ Verificando tipos..."
    mypy core/ --ignore-missing-imports || echo "⚠️ Avisos de tipo"

- name: 🧪 Executar testes
  run: |
    echo "🧪 Executando testes..."
    pytest tests/ -v --cov=core --cov-report=xml
```

## 🔧 Resolução de Problemas

### Erro: "black: command not found"
```bash
pip install black
# OU
python -m pip install black
```

### Erro: "No module named 'core'"
```bash
# Instalar em modo desenvolvimento
pip install -e .
# OU
pip install -e ".[dev]"
```

### Erro: Mock não funciona nos testes
```bash
# Verificar se o patch está no local correto
@patch('core.event_hub_client.AzureServiceBusRepository')  # ✅ Correto
@patch('core.azure.azure_service_bus_repository.AzureServiceBusRepository')  # ❌ Incorreto
```

### Erro: MyPy - Python version not supported
```bash
# Atualizar configuração no pyproject.toml
[tool.mypy]
python_version = "3.9"  # Mínimo suportado
```

## 📈 Melhorando a Cobertura

### Identificar código não coberto:
```bash
# Gerar relatório detalhado
pytest --cov=core --cov-report=html
# Abrir htmlcov/index.html no navegador
```

### Adicionar testes para funções não cobertas:
1. Identifique linhas vermelhas no relatório HTML
2. Crie testes específicos em `tests/`
3. Execute novamente para verificar melhoria

## 🎯 Checklist de Qualidade

Antes de fazer commit ou deploy:

- [ ] ✅ `black --check core/` passou
- [ ] ✅ `ruff check core/` passou  
- [ ] ✅ `mypy core/` passou (ou apenas avisos)
- [ ] ✅ `pytest tests/` passou
- [ ] ✅ Cobertura ≥ 80%
- [ ] ✅ `python -c "import core"` funciona
- [ ] ✅ Todos os imports estão corretos
- [ ] ✅ Documentação atualizada

## 🚨 Pipeline CI/CD

**Status esperados:**
- 🟢 **Verde**: Todos os checks passaram - deploy aprovado
- 🟡 **Amarelo**: Avisos de MyPy - deploy provavelmente OK  
- 🔴 **Vermelho**: Falhas críticas - deploy bloqueado

**Comandos que devem passar para deploy:**
```bash
# Estes 4 comandos DEVEM passar:
black --check core/                    # ✅ Formatação
ruff check core/                       # ✅ Qualidade  
pytest tests/ -v                       # ✅ Testes
python -c "import core; print('OK')"   # ✅ Imports

# Este pode ter avisos (não bloqueia):
mypy core/ --ignore-missing-imports    # ⚠️ Tipos
```

---

🎉 **Com este guia, sua pipeline de CI/CD passará sem problemas!**
# 🚀 Guia Completo de Deploy para PyPI

Este documento fornece instruções passo a passo para fazer o build e deploy do pacote `mentors-event-hub` para o PyPI.

## 📋 Pré-requisitos

### 1. Contas Necessárias
- **PyPI**: https://pypi.org/account/register/
- **TestPyPI** (opcional, para testes): https://test.pypi.org/account/register/

### 2. Ferramentas Necessárias
```bash
# Instalar dependências de build
pip install --upgrade pip
pip install build twine hatchling
```

## 🔐 Configuração de Tokens

### 1. Criar Token no PyPI

**Para PyPI (Produção):**
1. Acesse: https://pypi.org/manage/account/token/
2. Clique em **"Add API token"**
3. Preencha:
   - **Token name**: `mentors-event-hub-deploy`
   - **Scope**: Selecione "Entire account" ou específico para o projeto
4. Clique **"Add token"**
5. **COPIE O TOKEN** (formato: `pypi-AgEIcHlwaS5vcmcCJ...`)
6. **⚠️ IMPORTANTE**: Salve em local seguro, ele não será mostrado novamente

**Para TestPyPI (Testes):**
1. Acesse: https://test.pypi.org/manage/account/token/
2. Siga os mesmos passos acima
3. Token será similar: `pypi-AgEIcHlwaS5vcmcCJ...`

### 2. Configurar Tokens Localmente

**Opção 1 - Variáveis de Ambiente (Recomendado):**
```bash
# Para PyPI
export PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcCJ...SEU_TOKEN_AQUI"

# Para TestPyPI (opcional)
export PYPI_TEST_TOKEN="pypi-AgEIcHlwaS5vcmcCJ...SEU_TOKEN_TESTPYPI_AQUI"
```

**Opção 2 - Arquivo ~/.pypirc:**
```bash
# Criar arquivo de configuração
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...SEU_TOKEN_AQUI

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...SEU_TOKEN_TESTPYPI_AQUI
EOF

# Proteger o arquivo
chmod 600 ~/.pypirc
```

## 📦 Build e Deploy Manual

### 1. Preparação

```bash
# Navegar para o diretório do projeto
cd /opt/mentors_event_hub

# Verificar se está na branch correta
git branch
git status

# Limpar builds anteriores (se existirem)
rm -rf dist/ build/ *.egg-info/
```

### 2. Atualizar Versão

**Edite o arquivo `mentors_event_hub/__init__.py`:**
```python
# Antes
__version__ = "0.1.1"

# Depois (exemplo para versão 0.1.2)
__version__ = "0.1.2"
```

**Commit da nova versão:**
```bash
git add mentors_event_hub/__init__.py
git commit -m "🔖 Bump version to 0.1.2"
git push origin main
```

### 3. Build do Pacote

```bash
# Fazer build do pacote
python -m build

# Verificar arquivos gerados
ls -la dist/
# Você deve ver:
# - mentors_event_hub-0.1.2.tar.gz (source distribution)
# - mentors_event_hub-0.1.2-py3-none-any.whl (wheel distribution)
```

### 4. Validar Pacote

```bash
# Verificar se o pacote está correto
twine check dist/*

# Resultado esperado:
# Checking dist/mentors_event_hub-0.1.2.tar.gz: PASSED
# Checking dist/mentors_event_hub-0.1.2-py3-none-any.whl: PASSED
```

### 5. Deploy para TestPyPI (Recomendado primeiro)

```bash
# Upload para TestPyPI
twine upload --repository testpypi dist/*

# OU usando variável de ambiente
TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_TEST_TOKEN twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

**Testar instalação do TestPyPI:**
```bash
# Criar ambiente virtual para teste
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# test_env\Scripts\activate     # Windows

# Instalar do TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mentors-event-hub

# Testar importação
python -c "from core import EventHubClient; print('✅ Import funcionando!')"

# Limpar teste
deactivate
rm -rf test_env/
```

### 6. Deploy para PyPI (Produção)

```bash
# Upload para PyPI oficial
twine upload dist/*

# OU usando variável de ambiente
TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_TOKEN twine upload dist/*
```

**Verificar no PyPI:**
- Acesse: https://pypi.org/project/mentors-event-hub/
- Confirme que a nova versão está disponível

## 🛠️ Scripts Automatizados

### Script de Release Completo

**Criar arquivo `scripts/release.sh`:**
```bash
#!/bin/bash

set -e

echo "🚀 Iniciando processo de release..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para prints coloridos
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Verificar se está na branch main
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    print_error "Você deve estar na branch main para fazer release"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    print_error "Há mudanças não commitadas. Commit ou stash antes do release"
    git status --short
    exit 1
fi

# Verificar tokens
if [ -z "$PYPI_TOKEN" ]; then
    print_error "PYPI_TOKEN não configurado"
    echo "Configure com: export PYPI_TOKEN='seu-token-aqui'"
    exit 1
fi

print_success "Verificações iniciais passaram"

# Limpar build anterior
print_warning "Limpando builds anteriores..."
rm -rf dist/ build/ *.egg-info/

# Executar testes
print_warning "Executando testes..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v || {
        print_error "Testes falharam"
        exit 1
    }
    print_success "Testes passaram"
else
    print_warning "pytest não encontrado, pulando testes"
fi

# Verificar qualidade do código
print_warning "Verificando qualidade do código..."
if command -v black &> /dev/null; then
    black --check core/ || {
        print_error "Código não está formatado. Execute: black mentors_event_hub/"
        exit 1
    }
    print_success "Formatação verificada"
fi

if command -v ruff &> /dev/null; then
    ruff check core/ || {
        print_error "Problemas de linting encontrados"
        exit 1
    }
    print_success "Linting passou"
fi

# Build
print_warning "Fazendo build do pacote..."
python -m build || {
    print_error "Build falhou"
    exit 1
}
print_success "Build concluído"

# Verificar pacote
print_warning "Validando pacote..."
twine check dist/* || {
    print_error "Validação do pacote falhou"
    exit 1
}
print_success "Pacote validado"

# Mostrar arquivos gerados
echo ""
print_success "Arquivos gerados:"
ls -la dist/

# Confirmar upload
echo ""
read -p "🚀 Fazer upload para PyPI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Fazendo upload para PyPI..."
    TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_TOKEN twine upload dist/*
    print_success "Upload concluído!"
    
    # Obter versão
    VERSION=$(python -c "import core; print(core.__version__)")
    print_success "Nova versão disponível: https://pypi.org/project/mentors-event-hub/$VERSION/"
else
    print_warning "Upload cancelado"
fi

echo ""
print_success "Processo de release finalizado!"
```

**Tornar executável e usar:**
```bash
# Tornar executável
chmod +x scripts/release.sh

# Executar
./scripts/release.sh
```

## 🔧 Usando Makefile

**Criar `Makefile`:**
```makefile
.PHONY: clean build test upload upload-test release help

# Variáveis
PYTHON = python3
PIP = pip3
PACKAGE_NAME = mentors-event-hub

help: ## Mostrar ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

clean: ## Limpar arquivos de build
	@echo "🧹 Limpando arquivos de build..."
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install-dev: ## Instalar dependências de desenvolvimento
	@echo "📦 Instalando dependências de desenvolvimento..."
	$(PIP) install --upgrade pip
	$(PIP) install build twine hatchling
	$(PIP) install -e ".[dev]"

test: ## Executar testes
	@echo "🧪 Executando testes..."
	pytest tests/ -v --cov=core

lint: ## Verificar qualidade do código
	@echo "🔍 Verificando qualidade do código..."
	black --check core/
	ruff check core/
	mypy core/ --ignore-missing-imports

format: ## Formatar código
	@echo "🎨 Formatando código..."
	black mentors_event_hub/
	ruff --fix mentors_event_hub/

build: clean ## Fazer build do pacote
	@echo "🏗️ Fazendo build do pacote..."
	$(PYTHON) -m build
	@echo "📄 Arquivos criados:"
	@ls -la dist/

check: build ## Validar pacote
	@echo "✅ Validando pacote..."
	twine check dist/*

upload-test: check ## Upload para TestPyPI
	@echo "🧪 Fazendo upload para TestPyPI..."
	@if [ -z "$$PYPI_TEST_TOKEN" ]; then \
		echo "❌ PYPI_TEST_TOKEN não configurado"; \
		exit 1; \
	fi
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$PYPI_TEST_TOKEN twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload: check ## Upload para PyPI
	@echo "🚀 Fazendo upload para PyPI..."
	@if [ -z "$$PYPI_TOKEN" ]; then \
		echo "❌ PYPI_TOKEN não configurado"; \
		exit 1; \
	fi
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$PYPI_TOKEN twine upload dist/*

release: test lint upload ## Release completo (testes + lint + upload)
	@echo "🎉 Release concluído!"

version: ## Mostrar versão atual
	@$(PYTHON) -c "import mentors_event_hub; print(f'Versão atual: {mentors_event_hub.__version__}')"
```

**Usar o Makefile:**
```bash
# Ver comandos disponíveis
make help

# Release completo
make release

# Apenas upload para teste
make upload-test

# Build e validação
make check
```

## 🚨 Resolução de Problemas

### Erro: "Invalid or non-existent authentication information"
```bash
# Verificar se o token está correto
echo $PYPI_TOKEN  # Deve começar com "pypi-"

# Testar token manualmente
twine upload --repository testpypi dist/* --verbose
```

### Erro: "Package already exists"
- **Causa**: Tentativa de upload da mesma versão
- **Solução**: Incrementar versão em `__init__.py`

### Erro: "Invalid distribution filename"
```bash
# Limpar e rebuild
rm -rf dist/ build/ *.egg-info/
python -m build
```

### Erro: "Repository not found"
```bash
# Verificar URLs
# PyPI: https://upload.pypi.org/legacy/
# TestPyPI: https://test.pypi.org/legacy/
```

## 🎯 Checklist de Release

- [ ] Código testado e funcionando
- [ ] Versão incrementada em `__init__.py`
- [ ] Changelog atualizado (se aplicável)
- [ ] Token do PyPI configurado
- [ ] Build limpo (`rm -rf dist/`)
- [ ] Testes executados com sucesso
- [ ] Pacote validado com `twine check`
- [ ] Upload para TestPyPI (opcional)
- [ ] Teste de instalação do TestPyPI
- [ ] Upload para PyPI produção
- [ ] Verificação no https://pypi.org/project/mentors-event-hub/
- [ ] Tag e release no GitHub
- [ ] Documentação atualizada

## 📞 Suporte

Em caso de problemas:
1. Consulte os logs detalhados com `--verbose`
2. Verifique a documentação oficial: https://packaging.python.org/
3. Abra uma issue: https://github.com/mentorstec/mentors-event-hub/issues

---

🚀 **Boa sorte com seu deploy!**
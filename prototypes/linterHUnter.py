import requests
import base64
import time

# 1. COLOQUE SEU TOKEN AQUI
GITHUB_TOKEN = ""

# 2. LISTA APENAS DOS REPOSITÓRIOS QUE DERAM "No/Check" EM CODE MANAGEMENT
REPOSITORIOS_PENDENTES = [
    "python-hyper/h11",
    "fastapi/fastapi",
    "pypa/wheel",
    "pypa/packaging",
    "kjd/idna",
    "fsspec/s3fs",
    "pyparsing/pyparsing",
    "tartley/colorama",
    "jpadilla/pyjwt",
    "python-cffi/cffi",
    "benjaminp/six",
    "aio-libs/frozenlist",
    "python-attrs/attrs",
    "aio-libs/multidict",
    "encode/httpx",
    "scipy/scipy",
    "boto/s3transfer",
    "pytest-dev/iniconfig",
    "stub42/pytz",
    "giampaolo/psutil",
    "pypa/setuptools",
    "aws/aws-cli",
    "aio-libs/aiohttp",
    "jmespath/jmespath.py",
    "pygments/pygments",
    "python-jsonschema/jsonschema-specifications",
    "python-pillow/Pillow",
    "boto/boto3",
    "pypa/virtualenv",
    "open-telemetry/opentelemetry-python"
]

# Ferramentas de linting/formatação que vamos procurar
LINTERS = ["flake8", "black", "ruff", "isort", "mypy", "pylint"]

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_content(repo, path):
    """Busca um arquivo específico na API do GitHub."""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        if 'content' in data:
            return base64.b64decode(data['content']).decode('utf-8', errors='ignore')
    return None

def get_workflows(repo):
    """Lista e baixa todos os arquivos YAML dentro de .github/workflows."""
    url = f"https://api.github.com/repos/{repo}/contents/.github/workflows"
    resp = requests.get(url, headers=HEADERS)
    workflows = {}

    if resp.status_code == 200:
        files = resp.json()
        for file in files:
            if file['name'].endswith(('.yml', '.yaml')):
                content = get_file_content(repo, file['path'])
                if content:
                    workflows[file['path']] = content
    return workflows

print("Iniciando varredura por linters nos workflows...\n" + "-"*50)

for repo in REPOSITORIOS_PENDENTES:
    print(f"[{repo}] Buscando...")
    workflows = get_workflows(repo)
    encontrou_linter = False
    linter_encontrado = []

    for path, content in workflows.items():
        content_lower = content.lower()

        for linter in LINTERS:
            # Procuramos pela palavra isolada ou rodando como comando
            if linter in content_lower:
                if linter not in linter_encontrado:
                    linter_encontrado.append(linter)
                encontrou_linter = True

    if encontrou_linter:
        ferramentas = ", ".join(linter_encontrado)
        print(f"  ✅ YES (CI automated) -> Ferramentas encontradas: {ferramentas}")
    else:
        print(f"  ❌ NO -> Nenhuma ferramenta padrão encontrada nos workflows.")

    time.sleep(1) # Pausa para não bloquear a API

print("\n" + "-"*50 + "\nVarredura concluída!")

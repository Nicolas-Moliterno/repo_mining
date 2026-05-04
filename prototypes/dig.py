import requests
import base64
import csv
import time

# 1. COLOQUE SEU TOKEN AQUI PARA NÃO SER BLOQUEADO PELO GITHUB
GITHUB_TOKEN = ""

# 2. LISTA DE REPOSITÓRIOS PARA TESTAR
REPOSITORIOS = [
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

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_content(repo, path):
    """Tenta buscar um arquivo específico na branch principal do repo."""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        if 'content' in data:
            return base64.b64decode(data['content']).decode('utf-8', errors='ignore')
    return None

def get_workflows(repo):
    """Lista todos os arquivos dentro de .github/workflows e retorna seus conteúdos."""
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

def analyze_repo(repo):
    print(f"[{repo}] Analisando...")
    repo_data = {
        "Repositorio": repo,
        "CI Testing Integrated?": "No/Manual Check",
        "CD Present?": "No",
        "Deployment Tool": "None",
        "Deployment Tool Location": "None",
        "Code Management Automated?": "No/Manual Check",
        "Provisioning Tools": "N/A",
        "Versioning Automated?": "No/Manual Check",
        "Versioning Strategy": "Check Releases (Usually SemVer)"
    }

    # --- 1. Verificando Automação de Código (Linters/Pre-commit) ---
    if get_file_content(repo, ".pre-commit-config.yaml"):
        repo_data["Code Management Automated?"] = "Yes (pre-commit)"

    # --- 2. Verificando Versionamento Automático ---
    pyproject_content = get_file_content(repo, "pyproject.toml")
    setup_content = get_file_content(repo, "setup.py")

    if pyproject_content and ("setuptools_scm" in pyproject_content or "tbump" in pyproject_content):
        repo_data["Versioning Automated?"] = "Yes"
    elif setup_content and ("setuptools_scm" in setup_content):
        repo_data["Versioning Automated?"] = "Yes"

    # --- 3. Verificando CI e CD nos Workflows ---
    workflows = get_workflows(repo)

    for path, content in workflows.items():
        content_lower = content.lower()

        # Checar CI
        if "pytest" in content_lower or "tox" in content_lower or "nox" in content_lower:
            repo_data["CI Testing Integrated?"] = "Yes"

        # Checar CD (Deploy)
        if "pypa/gh-action-pypi-publish" in content_lower:
            repo_data["CD Present?"] = "Yes"
            repo_data["Deployment Tool"] = "gh-action-pypi-publish"
            repo_data["Deployment Tool Location"] = path
        elif "twine" in content_lower or "flit publish" in content_lower or "poetry publish" in content_lower:
            repo_data["CD Present?"] = "Yes"
            repo_data["Deployment Tool"] = "CLI tools (twine/flit/poetry)"
            repo_data["Deployment Tool Location"] = path

    return repo_data

# Execução Principal
resultados = []
for repo in REPOSITORIOS:
    dados = analyze_repo(repo)
    resultados.append(dados)
    time.sleep(1) # Pausa amigável para não sobrecarregar a API

# Salvando em CSV
colunas = [
    "Repositorio", "CI Testing Integrated?", "CD Present?",
    "Deployment Tool", "Deployment Tool Location",
    "Code Management Automated?", "Provisioning Tools",
    "Versioning Automated?", "Versioning Strategy"
]

nome_arquivo = "analise_repositorios_completa.csv"
with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=colunas)
    writer.writeheader()
    writer.writerows(resultados)

print(f"\nSucesso! Abra o arquivo '{nome_arquivo}' no Excel ou Google Sheets.")

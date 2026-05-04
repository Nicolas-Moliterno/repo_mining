import requests
import base64
import csv
import time

# 1. COLOQUE SEU TOKEN DO GITHUB AQUI
GITHUB_TOKEN = ""

# 2. LISTA DE REPOSITÓRIOS
REPOSITORIOS = [
    "python-hyper/h11", "fastapi/fastapi", "pypa/wheel", "pypa/packaging",
    "kjd/idna", "fsspec/s3fs", "pyparsing/pyparsing", "tartley/colorama",
    "jpadilla/pyjwt", "python-cffi/cffi", "benjaminp/six", "aio-libs/frozenlist",
    "python-attrs/attrs", "aio-libs/multidict", "encode/httpx", "scipy/scipy",
    "boto/s3transfer", "pytest-dev/iniconfig", "stub42/pytz", "giampaolo/psutil",
    "pypa/setuptools", "aws/aws-cli", "aio-libs/aiohttp", "jmespath/jmespath.py",
    "pygments/pygments", "python-jsonschema/jsonschema-specifications",
    "python-pillow/Pillow", "boto/boto3", "pypa/virtualenv", "open-telemetry/opentelemetry-python"
]

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_content(repo, path):
    """Busca o conteúdo de um arquivo na API do GitHub e decodifica de Base64."""
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

def analyze_cd(repo):
    print(f"[{repo}] Analisando CD...")
    repo_data = {
        "Repo Name": repo.split('/')[-1], # Pega só o nome do repo (ex: fastapi)
        "CD Present?": "No",
        "What is the deployment tool?": "-",
        "Where is the deployment tool defined?": "-"
    }

    workflows = get_workflows(repo)

    for path, content in workflows.items():
        content_lower = content.lower()

        # Action oficial do GitHub para PyPI
        if "pypa/gh-action-pypi-publish" in content_lower:
            repo_data["CD Present?"] = "Yes"
            repo_data["What is the deployment tool?"] = "pypa/gh-action-pypi-publish"
            repo_data["Where is the deployment tool defined?"] = f"{repo.split('/')[-1]}/{path}"
            break # Já achou, pode pular para o próximo repo

        # Ferramentas CLI
        elif "twine" in content_lower:
            repo_data["CD Present?"] = "Yes"
            repo_data["What is the deployment tool?"] = "twine"
            repo_data["Where is the deployment tool defined?"] = f"{repo.split('/')[-1]}/{path}"
            break
        elif "flit publish" in content_lower:
            repo_data["CD Present?"] = "Yes"
            repo_data["What is the deployment tool?"] = "flit"
            repo_data["Where is the deployment tool defined?"] = f"{repo.split('/')[-1]}/{path}"
            break
        elif "poetry publish" in content_lower:
            repo_data["CD Present?"] = "Yes"
            repo_data["What is the deployment tool?"] = "poetry"
            repo_data["Where is the deployment tool defined?"] = f"{repo.split('/')[-1]}/{path}"
            break
        elif "hatch publish" in content_lower:
            repo_data["CD Present?"] = "Yes"
            repo_data["What is the deployment tool?"] = "hatch"
            repo_data["Where is the deployment tool defined?"] = f"{repo.split('/')[-1]}/{path}"
            break
        elif "uv publish" in content_lower:
            repo_data["CD Present?"] = "Yes"
            repo_data["What is the deployment tool?"] = "astral_uv"
            repo_data["Where is the deployment tool defined?"] = f"{repo.split('/')[-1]}/{path}"
            break

    return repo_data

# --- Execução Principal ---
resultados = []
for repo in REPOSITORIOS:
    dados = analyze_cd(repo)
    resultados.append(dados)
    time.sleep(1) # Pausa para não estourar o limite de requisições da API

# --- Salvando os Resultados ---
colunas = ["Repo Name", "CD Present?", "What is the deployment tool?", "Where is the deployment tool defined?"]
nome_arquivo = "analise_cd_repos.csv"

with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=colunas)
    writer.writeheader()
    writer.writerows(resultados)

print(f"\nConcluído! Arquivo '{nome_arquivo}' gerado com sucesso.")

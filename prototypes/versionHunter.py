import requests
import base64
import csv
import time
import re

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
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        if 'content' in data:
            return base64.b64decode(data['content']).decode('utf-8', errors='ignore')
    return None

def get_latest_release_or_tag(repo):
    """Busca se o repo usa Github Releases ou apenas Tags e retorna a última versão."""
    info = {"type": [], "latest_tag": ""}

    # Checa GitHub Releases
    resp_rel = requests.get(f"https://api.github.com/repos/{repo}/releases?per_page=1", headers=HEADERS)
    if resp_rel.status_code == 200 and resp_rel.json():
        info["type"].append("Github Releases")
        info["latest_tag"] = resp_rel.json()[0].get("tag_name", "")

    # Checa Tags se não tiver release, ou adiciona como complementar
    resp_tags = requests.get(f"https://api.github.com/repos/{repo}/tags?per_page=1", headers=HEADERS)
    if resp_tags.status_code == 200 and resp_tags.json():
        if "Github Releases" not in info["type"]:
            info["type"].append("Release Tags")
        if not info["latest_tag"]:
            info["latest_tag"] = resp_tags.json()[0].get("name", "")

    return info

def analyze_env_and_version(repo):
    print(f"[{repo}] Coletando dados...")
    repo_data = {
        "Repo Name": repo.split('/')[-1],
        "Configuration and Provisioning tools": "",
        "Is Versioning automated?": "No",
        "Versioning Strategy": ""
    }

    # --- 1. CONFIGURATION AND PROVISIONING TOOLS ---
    env_tools = []
    pyproject = get_file_content(repo, "pyproject.toml") or ""
    setup_py = get_file_content(repo, "setup.py") or ""

    if get_file_content(repo, "tox.ini") or "tool.tox" in pyproject:
        env_tools.append("tox")
    if get_file_content(repo, "noxfile.py"):
        env_tools.append("nox")
    if "tool.poetry" in pyproject:
        env_tools.append("poetry")
    if "hatch" in pyproject:
        env_tools.append("hatch")
    if "pdm" in pyproject:
        env_tools.append("pdm")
    if get_file_content(repo, "Pipfile"):
        env_tools.append("pipenv")

    # Fallback genérico para ecossistema Python
    if not env_tools:
        env_tools.append("pip/venv")

    repo_data["Configuration and Provisioning tools"] = ", ".join(env_tools)

    # --- 2. IS VERSIONING AUTOMATED? ---
    # Ferramentas que extraem a versão da Tag do Git ou dão bump automático
    auto_tools = ["setuptools_scm", "hatch-vcs", "poetry-dynamic-versioning", "tbump", "bumpversion", "bump2version"]
    if any(tool in pyproject for tool in auto_tools) or any(tool in setup_py for tool in auto_tools):
        repo_data["Is Versioning automated?"] = "Yes"

    # --- 3. VERSIONING STRATEGY ---
    version_info = get_latest_release_or_tag(repo)
    strategy_parts = version_info["type"]
    tag = version_info["latest_tag"]

    if tag:
        # Checa se é Calendar Versioning (ex: 2023.1, 2024.10.1)
        if re.search(r'^v?20[12]\d\.\d+', tag):
            strategy_parts.append("Calendar Versioning (CalVer)")
        # Checa se é Semantic Versioning (ex: 1.2.3, v2.0.0)
        elif re.search(r'^v?\d+\.\d+', tag):
            strategy_parts.append("Semantic Versioning")
    else:
        strategy_parts.append("Semantic Versioning (Assumed)")

    repo_data["Versioning Strategy"] = ", ".join(strategy_parts)

    return repo_data

# --- Execução Principal ---
resultados = []
for repo in REPOSITORIOS:
    dados = analyze_env_and_version(repo)
    resultados.append(dados)
    time.sleep(1) # Pausa da API

# --- Salvando em CSV ---
colunas = ["Repo Name", "Configuration and Provisioning tools", "Is Versioning automated?", "Versioning Strategy"]
nome_arquivo = "analise_env_versao.csv"

with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=colunas)
    writer.writeheader()
    writer.writerows(resultados)

print(f"\nFinalizado! As 3 colunas foram preenchidas no arquivo '{nome_arquivo}'.")

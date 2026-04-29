import csv
import re
import subprocess
import tempfile
from pathlib import Path

REPOS = [
    "https://github.com/boto/boto3",
    "https://github.com/pypa/packaging",
    "https://github.com/pypa/setuptools",
    "https://github.com/urllib3/urllib3",
    "https://github.com/certifi/python-certifi",
    "https://github.com/python/typing_extensions",
    "https://github.com/psf/requests",
    "https://github.com/jawah/charset_normalizer",
    "https://github.com/kjd/idna",
    "https://github.com/boto/botocore",
    "https://github.com/aio-libs/aiobotocore",
    "https://github.com/dateutil/dateutil",
    "https://github.com/pyca/cryptography",
    "https://github.com/benjaminp/six",
    "https://github.com/numpy/numpy",
    "https://github.com/python-cffi/cffi",
    "https://github.com/yaml/pyyaml",
    "https://github.com/grpc/grpc",
    "https://github.com/eliben/pycparser",
    "https://github.com/pydantic/pydantic",
    "https://github.com/pytest-dev/pluggy",
    "https://github.com/boto/s3transfer",
    "https://github.com/pygments/pygments",
    "https://github.com/pallets/click",
    "https://github.com/python-attrs/attrs",
    "https://github.com/protocolbuffers/protobuf",
    "https://github.com/pydantic/pydantic/tree/main/pydantic-core",
    "https://github.com/agronholm/anyio",
    "https://github.com/fsspec/filesystem_spec",
    "https://github.com/pandas-dev/pandas",
    "https://github.com/pytest-dev/pytest",
    "https://github.com/python-hyper/h11",
    "https://github.com/pallets/markupsafe/",
    "https://github.com/pytest-dev/iniconfig",
    "https://github.com/fsspec/s3fs/",
    "https://github.com/tox-dev/platformdirs",
    "https://github.com/annotated-types/annotated-types",
    "https://github.com/pypa/pip",
    "https://github.com/pypa/wheel",
    "https://github.com/pallets/jinja/",
    "https://github.com/jmespath/jmespath.py",
    "https://github.com/python/importlib_metadata",
    "https://github.com/tox-dev/filelock",
    "https://github.com/cpburnz/python-pathspec",
    "https://github.com/jpadilla/pyjwt",
    "https://github.com/encode/httpx",
    "https://github.com/pydantic/typing-inspection",
    "https://github.com/theskumar/python-dotenv",
    "https://github.com/encode/httpcore",
    "https://github.com/stub42/pytz",
    "https://github.com/jaraco/zipp",
    "https://github.com/Textualize/rich",
    "https://github.com/pyasn1/pyasn1",
    "https://github.com/python-jsonschema/jsonschema",
    "https://github.com/aio-libs/yarl",
    "https://github.com/aio-libs/multidict",
    "https://github.com/aio-libs/aiohttp",
    "https://github.com/googleapis/google-auth-library-python",
    "https://github.com/Kludex/uvicorn",
    "https://github.com/executablebooks/markdown-it-py",
    "https://github.com/googleapis/google-cloud-python",
    "https://github.com/python/tzdata",
    "https://github.com/tqdm/tqdm",
    "https://github.com/hukkin/tomli",
    "https://github.com/tartley/colorama",
    "https://github.com/googleapis/google-cloud-python/tree/main/packages/googleapis-common-protos",
    "https://github.com/executablebooks/mdurl",
    "https://github.com/Kludex/starlette",
    "https://github.com/pypa/virtualenv",
    "https://github.com/aws/aws-cli",
    "https://github.com/python-pillow/Pillow",
    "https://github.com/aio-libs/propcache",
    "https://github.com/aio-libs/frozenlist",
    "https://github.com/scipy/scipy",
    "https://github.com/crate-py/rpds",
    "https://github.com/pypa/trove-classifiers",
    "https://github.com/fastapi/fastapi",
    "https://github.com/sybrenstuvel/python-rsa",
    "https://github.com/python-jsonschema/referencing",
    "https://github.com/GrahamDumpleton/wrapt",
    "https://github.com/pyasn1/pyasn1-modules",
    "https://github.com/aio-libs/aiosignal",
    "https://github.com/python-jsonschema/jsonschema-specifications",
    "https://github.com/python-greenlet/greenlet",
    "https://github.com/grpc/grpc",
    "https://github.com/sqlalchemy/sqlalchemy",
    "https://github.com/requests/requests-oauthlib",
    "https://github.com/apache/arrow",
    "https://github.com/pyparsing/pyparsing",
    "https://github.com/aio-libs/aiohappyeyeballs",
    "https://github.com/open-telemetry/opentelemetry-python",
    "https://github.com/jd/tenacity",
    "https://github.com/fastapi/annotated-doc",
    "https://github.com/tkem/cachetools/",
    "https://github.com/mrabarnett/mrab-regex",
    "https://github.com/giampaolo/psutil",
    "https://github.com/open-telemetry/opentelemetry-python",
    "https://github.com/pypa/hatch",
    "https://github.com/oauthlib/oauthlib",
    "https://github.com/open-telemetry/opentelemetry-python",

]

OUTPUT_FILE = "deployment_workflows.csv"

WORKFLOW_INCLUDE = ["publish", "release", "deploy"]

ACTIONS_PATTERNS = [
    r"pypa/gh-action-pypi-publish[^\s\"']*",
]

CLI_PATTERNS = [
    r"\btwine upload\b",
    r"\buv publish\b",
]

TOOL_MAP = {
    "uv publish":                    "astral_uv",
    "twine upload":                  "twine",
    "pypa/gh-action-pypi-publish":   "pypa",
}


def normalize(tool: str) -> str:
    for pattern, label in TOOL_MAP.items():
        if tool.startswith(pattern):
            return label
    return tool


def extract_tools(content: str) -> list[str]:
    found = set()

    for pattern in ACTIONS_PATTERNS:
        for match in re.findall(pattern, content):
            found.add(match.strip())

    run_blocks = re.findall(r"run:\s*\|?([\s\S]*?)(?=\n\s*\w+:|$)", content)
    for block in run_blocks:
        for pattern in CLI_PATTERNS:
            match = re.search(pattern, block)
            if match:
                found.add(match.group().strip())

    return sorted(normalize(t) for t in found)


def mine_repos(repos: list[str]) -> list[dict]:
    rows = []
    for idx, repo_url in enumerate(repos):
        print(f"\n-> Mining: {repo_url} ({idx+1}/{len(repos)})")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["git", "clone", "--depth=1", repo_url, tmpdir],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"  git clone failed:\n{result.stderr.strip()}")
                continue

            workflow_dir = Path(tmpdir) / ".github" / "workflows"
            if not workflow_dir.exists():
                print("  No .github/workflows/ found.")
                continue

            tools = []
            for wf_file in sorted(workflow_dir.glob("*.y*ml")):
                if not any(kw in wf_file.name.lower() for kw in WORKFLOW_INCLUDE):
                    continue

                content = wf_file.read_text(encoding="utf-8", errors="ignore")
                tools = extract_tools(content)
                rel = str(wf_file.relative_to(Path(tmpdir)))

                print(f"  {rel} | {tools or '-'}")

                rows.append({
                    "repo":          repo_url,
                    "workflow_file": rel,
                    "tools":         ", ".join(tools) if tools else "-",
                })
            
            if len(tools) == 0:
                rows.append({
                    "repo":          repo_url,
                    "workflow_file": "-",
                    "tools":         "-",
                })
                print(f"  - | - ") 

    return rows


def save_csv(rows: list[dict], path: str) -> None:
    if not rows:
        print("Nothing found.")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n✓ Saved {len(rows)} rows -> {path}")


if __name__ == "__main__":
    results = mine_repos(REPOS)
    save_csv(results, OUTPUT_FILE)

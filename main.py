import os
import subprocess
import urllib.request
import json
import ssl
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn

app = FastAPI()
PROJECT_REPO_DIR_MAP = json.loads(os.environ.get("PROJECT_REPO_DIR_MAP", "{}"))
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
HTTPS_PROXY_URL = os.environ["HTTPS_PROXY_URL"]
SERVER_HOST = os.environ["SERVER_HOST"]
SERVER_PORT = int(os.environ["SERVER_PORT"])
SERVER_LOG_LEVEL = os.environ["SERVER_LOG_LEVEL"]
PROMPT_PATH = Path(__file__).parent / "codex-prompt.txt"

@app.post("/webhook/gitlab")
async def gitlab_webhook_wrapper(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    background_tasks.add_task(gitlab_webhook, payload)

    return {"status": "ok"}

def gitlab_webhook(payload: Any):
    print(json.dumps(payload, ensure_ascii=False))

    print(f"Webhook event: {payload.get('object_kind')}")

    project_name = payload["project"]["name"]
    repo_dir = PROJECT_REPO_DIR_MAP.get(project_name)
    if not repo_dir:
        return {"status": "ok", "event": payload.get("object_kind")}

    branch_name = payload["ref"].replace("refs/heads/", "")
    project_name_for_file = project_name.replace("/", "_").replace(" ", "_")
    output_path = Path("/tmp") / f"codex-output-{project_name_for_file}.txt"
    commit_ids = [commit["id"] for commit in payload["commits"]]
    commit_ids_for_prompt = " ".join(commit_ids)
    subprocess.run(["git", "fetch", "origin"], cwd=repo_dir, check=False)
    subprocess.run(["git", "checkout", "-B", branch_name], cwd=repo_dir, check=False)

    codex_prompt = PROMPT_PATH.read_text()
    codex_prompt = codex_prompt.replace("$branch_name", branch_name)
    codex_prompt = codex_prompt.replace("$commit_ids", commit_ids_for_prompt)
    codex_prompt = codex_prompt.replace("$output_path", str(output_path))
    codex_env = dict(os.environ)
    codex_env["HTTPS_PROXY"] = HTTPS_PROXY_URL

    codex_output = "Gitlab onpush reviewer: Codex run failed"
    try:
        subprocess.check_output(
            [
                "codex",
                "--model",
                "gpt-5.3-codex",
                "--ask-for-approval",
                "never",
                "exec",
                codex_prompt,
            ],
            cwd=repo_dir,
            text=True,
            env=codex_env,
        ).strip()
        codex_output = output_path.read_text()
    except subprocess.CalledProcessError:
        print("Codex run failed")

    codex_output = f"Project: {project_name}\n{codex_output}"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    telegram_payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": codex_output}).encode("utf-8")
    telegram_request = urllib.request.Request(
        telegram_url,
        data=telegram_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(telegram_request, context=ssl._create_unverified_context())

    return {"status": "ok", "event": payload.get("object_kind")}

@app.get("/webhook/gitlab/test")
async def gitlab_webhook_test():
    class FakeRequest:
        async def json(self):
            return {
                "object_kind": "test",
                "ref": "refs/heads/main",
                "project": {"name": "mldub"},
                "commits": [{"id": "test"}],
            }

    return await gitlab_webhook(FakeRequest())


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level=SERVER_LOG_LEVEL,
        access_log=True,
    )

# onpush

AI-powered reviewer for Git workflow.

Watches configured set of Gitlab repositories, prepares and sends reports to Telegram channel. 

Uses [OpenAI Codex](https://openai.com/codex/) as the code review agent.

## How It Works

1. Receives a push event from Gitlab.
2. Fetches repository for specified project.
3. Runs OpenAI Codex CLI to examine the latest changes and compile a short report.
4. Sends the report to the configured Telegram chat.

## Install & Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-dotenv
cp .env.example .env
```

Install and configure  OpenaAI Codex separately using the official OpenAI docs: https://openai.com/codex/

## Configuration

The service loads variables from `.env`.

- `PROJECT_REPO_DIR_MAP`: JSON object mapping GitLab project names to local repository paths
- `TELEGRAM_BOT_TOKEN`: Telegram bot token used to send notifications
- `TELEGRAM_CHAT_ID`: Telegram chat or channel ID
- `HTTPS_PROXY_URL`: proxy URL passed to Codex as `HTTPS_PROXY`
- `SERVER_HOST`: host used by Uvicorn
- `SERVER_PORT`: port used by Uvicorn

Example values are provided in [`.env.example`](/Users/korytov/projects/onpush/.env.example).

## Add a New Repo to Reviewer

To make the reviewer process another repository, add a new entry to `PROJECT_REPO_DIR_MAP` in `.env`.

Example:

```dotenv
PROJECT_REPO_DIR_MAP={"project-a":"/path/to/project-a","project-b":"/path/to/project-b","new-project":"/path/to/new-project"}
```

Requirements:

- The key must exactly match the GitLab project name from the webhook payload.
- The value must be an absolute path to the local clone on this machine.
- The local repository must already exist and have an `origin` remote, because the service runs `git fetch origin`.

After updating `.env`, restart the service so the new mapping is loaded.

## Run

```bash
python main.py
```

The app starts a Uvicorn server using the host, port, and log level from `.env`.

## Endpoints

- `POST /webhook/gitlab`: main webhook endpoint

## OpenAI Codex References

- [Codex product page](https://openai.com/codex/)
- [Introducing Codex](https://openai.com/index/introducing-codex/)
- [Codex cloud docs](https://platform.openai.com/docs/codex/overview)
- [Docs MCP](https://platform.openai.com/docs/docs-mcp)

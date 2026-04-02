# onpush

AI-powered Git commit reviewer.

This service watches a configured set of GitLab repositories, generates review reports on committed changes, and sends them to a Telegram channel.

Uses [OpenAI Codex](https://openai.com/codex/) as the code review agent.

## How It Works

1. Receives a push event from GitLab.
2. Fetches the repository for the specified project.
3. Runs OpenAI Codex CLI to examine the latest changes and compile a short report.
4. Sends the report to the configured Telegram chat.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-dotenv
cp .env.example .env
```

Install and configure OpenAI Codex separately by following the official docs:

- [OpenAI Codex](https://openai.com/codex/)

## Configuration

The service loads variables from `.env`.

- `PROJECT_REPO_DIR_MAP`: JSON object mapping GitLab project names to local repository paths
- `TELEGRAM_BOT_TOKEN`: Telegram bot token used to send notifications
- `TELEGRAM_CHAT_ID`: Telegram chat or channel ID
- `HTTPS_PROXY_URL`: proxy URL passed to Codex as `HTTPS_PROXY`
- `SERVER_HOST`: host used by Uvicorn
- `SERVER_PORT`: port used by Uvicorn

Example values are provided in [`.env.example`](.env.example).

## Add a New Repo to Reviewer

To make the reviewer process a repository, add a new entry to `PROJECT_REPO_DIR_MAP` in `.env`.

Example:

```dotenv
PROJECT_REPO_DIR_MAP={"project-a":"/path/to/project-a","project-b":"/path/to/project-b","new-project":"/path/to/new-project"}
```

Requirements:

- The key must exactly match the GitLab project name from the webhook payload.
- The value must be an absolute path to the local clone on this machine.
- The local repository must already exist and have an `origin` remote.

## Run

```bash
python main.py
```

## Endpoints

- `POST /webhook/gitlab`: main webhook endpoint

# Workspace Layout

Simple monorepo structure:

- `cpa/`: existing CLIProxyAPI source
- `drission-scraper/`: one direct DrissionPage signup flow script
- `docker-compose.yml`: single orchestration entrypoint

## What the scraper does

One run does this exact flow:

1. Open temp mail website and read generated email.
2. Open signup website and clear browser cache/cookies/session.
3. Input temp email and click send code.
4. Return to temp mail website and poll inbox for code.
5. Go back to signup site, input code, name, birthday, and submit.

No local storage or scraper pipeline system is used.

## Setup

1. Copy `.env.example` to `.env`.
2. Fill all selector variables for your target websites.
3. Start with:

```bash
docker compose up -d --build
```

## Important env vars

- `SIGNUP_URL`
- `TEMP_MAIL_URL`
- `TEMP_EMAIL_SELECTOR`
- `TEMP_EMAIL_BODY_SELECTOR`
- `SIGNUP_EMAIL_SELECTOR`
- `SIGNUP_SEND_CODE_SELECTOR`
- `SIGNUP_CODE_SELECTOR`
- `SIGNUP_NAME_SELECTOR`
- `SIGNUP_BIRTHDAY_SELECTOR`
- `SIGNUP_SUBMIT_SELECTOR`
- `PROFILE_NAME`
- `PROFILE_BIRTHDAY`
- `MAX_SIGNUPS`
# cli-proxy-api

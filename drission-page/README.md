# Drission Scraper

This is a single direct signup flow script in `app/main.py`.

Flow per signup:

1. Read temp email from temp mail website.
2. Clear cache/cookies/session on signup site.
3. Fill email and request verification code.
4. Go back to temp mail website and fetch code from email body.
5. Fill code, name, birthday and submit.

## Flow modes

- `FLOW_MODE=open_temp_mail_only`: open temp mail website and optionally read email text.
- `FLOW_MODE=full_signup`: run the full signup flow.

Default mode is `open_temp_mail_only`.

For `open_temp_mail_only`, you must set:

- `TEMP_EMAIL_SELECTOR`

Optional:

- `TEMP_GENERATE_BTN_SELECTOR` (if the site needs a click to generate/refresh mailbox)

## Required environment variables (full_signup)

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

## Optional variables

- `HEADLESS` (default `true`)
- `FLOW_MODE` (default `open_temp_mail_only`)
- `EMAIL_CODE_REGEX` (default `(\d{6})`)
- `EMAIL_WAIT_TIMEOUT_SECONDS` (default `120`)
- `EMAIL_POLL_SECONDS` (default `5`)
- `MAX_SIGNUPS` (default `1`)
- `BETWEEN_SIGNUP_DELAY_SECONDS` (default `15`)

## Run

Use root compose:

```bash
docker compose up -d --build drission-scraper
```

Run locally with uv:

```bash
cd drission-scraper
uv sync
FLOW_MODE=open_temp_mail_only uv run --env-file ../.env python -m app.main
```

Install a new package:

```bash
uv add <package>
```

Install a new dev package:

```bash
uv add --dev <package>
```

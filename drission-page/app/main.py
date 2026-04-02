import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv

from DrissionPage import ChromiumOptions, ChromiumPage


env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _require(name: str) -> str:
    value = _env(name)
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def _create_page() -> ChromiumPage:
    headless = _env("HEADLESS", "true").lower() == "true"
    opts = ChromiumOptions()
    
    opts.set_browser_path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    opts.set_local_port(9333)
    opts.auto_port()
    
    if headless:
        opts.headless(True)
    
    return ChromiumPage(addr_or_opts=opts)


def _clear_session(page: ChromiumPage) -> None:
    # Keep each signup isolated from previous state.
    try:
        page.run_cdp("Network.clearBrowserCookies")
        page.run_cdp("Network.clearBrowserCache")
    except Exception:
        pass
    page.run_js("localStorage.clear(); sessionStorage.clear();")


def _open_temp_mail_only(page: ChromiumPage) -> None:
    temp_mail_url = _env("TEMP_MAIL_URL")
    generate_btn_selector = _env("TEMP_GENERATE_BTN_SELECTOR")
    temp_email_selector = _env("TEMP_EMAIL_SELECTOR")

    page.get(temp_mail_url)
    print(f"[drission-scraper] opened temp mail url: {temp_mail_url}")

    # Step 1: Click the generate button
    try:
        btn = page.ele(generate_btn_selector, timeout=10)
        btn.click()
        print("[drission-scraper] clicked generate button")
        time.sleep(1) 
    except Exception as e:
        print(f"[drission-scraper] failed to click generate button: {e}")

    # Step 2: Extract the email
    if temp_email_selector:
        temp_email = page.ele(temp_email_selector, timeout=5).text.strip()
        if temp_email:
            print(f"[drission-scraper] temp email: {temp_email}")
            return temp_email
        else:
            print("[drission-scraper] temp email selector found but email text is empty")
    else:
        print("[drission-scraper] TEMP_EMAIL_SELECTOR not set, skipping email extraction")


def _extract_code(text: str, regex_pattern: str) -> str:
    match = re.search(regex_pattern, text)
    if not match:
        raise RuntimeError("Verification code not found in email body")
    return match.group(1)


def _wait_for_email_code(
    page: ChromiumPage,
    temp_mail_url: str,
    email_address: str,
    email_body_selector: str,
    code_regex: str,
    timeout_seconds: int,
    poll_seconds: int,
) -> str:
    specific_mail_url = f"{temp_mail_url.rstrip('/')}/{email_address}"
    deadline = time.time() + timeout_seconds

    print(f"[drission-scraper] monitoring inbox: {specific_mail_url}")

    while time.time() < deadline:
        try:
            # Hard reload the page every iteration — avoids stale element issues entirely
            page.get(specific_mail_url)
            time.sleep(2)

            body_ele = page.ele(email_body_selector, timeout=3)
            if body_ele:
                body_text = body_ele.text.strip()
                print(f"[drission-scraper] email content found: {body_text}")
                if body_text:
                    try:
                        return _extract_code(body_text, code_regex)
                    except RuntimeError:
                        print("[drission-scraper] code not found in body yet, retrying...")
            else:
                print("[drission-scraper] no email yet, retrying...")

        except Exception as e:
            print(f"[drission-scraper] polling update: {e}")

        time.sleep(poll_seconds)

    raise TimeoutError("Timed out waiting for verification email code")

def _handle_signup_modal(tab, email: str) -> None:
    # 1. Wait for the page to actually settle
    print("[drission-scraper] waiting for page load...")
    tab.wait.load_start()
    time.sleep(2)

    # 2. Try to find the button using multiple strategies
    login_btn = tab.ele('@@data-testid=login-button', timeout=5)
    
    if not login_btn:
        print("[drission-scraper] data-testid failed, trying text-based search...")
        login_btn = tab.ele('text=Log in', timeout=5)

    if not login_btn:
        raise RuntimeError("Could not find Log In button using ID or Text.")

    print("[drission-scraper] clicking login button")
    login_btn.click()

    # 3. Wait for Modal Input
    print(f"[drission-scraper] entering email: {email}")
    # Using a relative search for the email input
    email_input = tab.ele('@id=email', timeout=10)
    email_input.input(email)

    # 4. Click Continue
    print("[drission-scraper] clicking continue")
    # Using the text inside the button as the anchor
    tab.ele('text=Continue', timeout=10).click()

    # 5. NEW STEP: Enter Password
    print("[drission-scraper] entering password: qwerty123456")
    pass_field = tab.ele('@type=password', timeout=10)
    if not pass_field:
        # Fallback to searching for the label text you provided
        pass_field = tab.ele('text=Password').parent().ele('tag:input')
        
    pass_field.input("qwerty123456")

    # 6. NEW STEP: Click Continue Again
    print("[drission-scraper] clicking continue (password step)")
    continue_after_pass = tab.ele('@@data-dd-action-name=Continue', timeout=10)
    
    if not continue_after_pass:
        # Fallback to the generic submit button if the action-name fails
        continue_after_pass = tab.ele('@@type=submit@text()=Continue')

    continue_after_pass.click()

import random

import random

def _finalize_signup(tab, code: str) -> None:
    # 1. Input the Verification Code
    print(f"[drission-scraper] entering verification code: {code}")
    tab.ele('@name=code', timeout=10).input(code)

    # Click Continue (Validation step)
    print("[drission-scraper] validating code...")
    tab.ele('@@name=intent@@value=validate').click()

    # 2. Generate Random Identity
    first_names = ["James", "Robert", "John", "Michael", "David", "William", "Richard", "Joseph", "Thomas", "Christopher"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # Generate a random birthday (e.g., between 1990 and 2005)
    year = str(random.randint(1990, 2005))
    month = str(random.randint(1, 12)).zfill(2)
    day = str(random.randint(1, 28)).zfill(2)

    # 3. Input Name
    print(f"[drission-scraper] entering name: {full_name}")
    tab.ele('@name=name', timeout=10).input(full_name)

    # 4. Input Birthday Segments
    print(f"[drission-scraper] entering birthday: {month}/{day}/{year}")
    
    try:
        # Find the segments within the birthday container
        tab.ele('@@data-type=month').input(month)
        tab.ele('@@data-type=day').input(day)
        tab.ele('@@data-type=year').input(year)
    except Exception as e:
        print(f"[drission-scraper] Birthday segment input failed, trying simple age fallback: {e}")
        # If the UI falls back to a simple age field, you'd handle it here.

    # 5. Finish Creating Account
    print("[drission-scraper] clicking Finish creating account")
    # Using the button text as it's the most distinct part of the finish step
    finish_btn = tab.ele('text=Finish creating account', timeout=10)
    if not finish_btn:
         # Fallback to the Submit type if text differs
         finish_btn = tab.ele('@type=submit')
         
    finish_btn.click()


def run_once(page: ChromiumPage) -> None:
    # 1. Setup URLs
    signup_url = _require("SIGNUP_URL")
    temp_mail_url = _require("TEMP_MAIL_URL")
    email_body_selector = _require("TEMP_EMAIL_BODY_SELECTOR")
    
    # 2. Get the Email (Tab 0)
    mail_tab = page.get_tab(0)
    generated_email = _open_temp_mail_only(mail_tab)
    
    if not generated_email:
        raise RuntimeError("Failed to extract temp email")

    # 3. Open Signup in a NEW Tab and Clear Session
    signup_tab = page.new_tab(signup_url)
    _clear_session(signup_tab)

    # 4. Handle the Modal Signup Flow
    _handle_signup_modal(signup_tab, generated_email)

    # 5. Wait for Code (Switching focus to the mail tab)
    code_regex = _env("EMAIL_CODE_REGEX", r"(\d{6})")
    email_wait_timeout = int(_env("EMAIL_WAIT_TIMEOUT_SECONDS", "120"))
    email_poll_seconds = int(_env("EMAIL_POLL_SECONDS", "5"))

    # Pass the generated_email so the function knows which inbox to open
    code = _wait_for_email_code(
        page=mail_tab, 
        temp_mail_url=temp_mail_url,
        email_address=generated_email,
        email_body_selector=email_body_selector,
        code_regex=code_regex,
        timeout_seconds=email_wait_timeout,
        poll_seconds=email_poll_seconds,
    )

    # 6. Finalize Signup on the signup tab
    print(f"[drission-scraper] entering verification code: {code}")
    _finalize_signup(signup_tab, code)
    print(f"[drission-scraper] signup complete! email: {generated_email}")
    time.sleep(5)
    # signup_tab.close()


def main() -> None:
    page = _create_page()
    delay_seconds = int(_env("BETWEEN_SIGNUP_DELAY_SECONDS"))
    max_signups = int(_env("MAX_SIGNUPS"))

    print(f"[drission-scraper] starting signup flow, max_signups={max_signups}")

    success_count = 0
    for idx in range(max_signups):
        try:
            run_once(page)
            success_count += 1
            print(f"[drission-scraper] signup {idx + 1}/{max_signups} success")
        except Exception as exc:
            print(f"[drission-scraper] signup {idx + 1}/{max_signups} failed: {exc}")
        if idx < max_signups - 1:
            time.sleep(delay_seconds)

    print(f"[drission-scraper] done, success_count={success_count}")


if __name__ == "__main__":
    main()

"""Kindle quotes source using Selenium automation.

Handles login (including optional 2FA), navigates to Kindle Notebook, and
scrapes covers and highlights to build a local quotebook cache.

Environment overrides:
- QUOTESCAPE_BROWSER: preferred browser ('system','chrome','firefox','edge','safari')
- QUOTESCAPE_LOGIN_TIMEOUT: seconds to wait for login/2FA (default 300)
"""

import json
import logging
import os
import platform
import plistlib
from pathlib import Path
import random
from os import path
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
from importlib.resources import files, as_file
try:
    from selenium.webdriver.safari.options import Options as SafariOptions
except Exception:
    SafariOptions = None  # type: ignore

logger = logging.getLogger(__name__)


class KindleQuotes:
    """Fetch quotes and covers from Kindle Notebook.

    Parameters:
    - quotebook_path: where to write/read the JSON cache
    - update_after: days after which the cache is considered stale
    - browser: preferred browser name or 'system' (macOS default) detection
    - login_timeout: seconds to wait for login/2FA to complete
    """

    def __init__(self, quotebook_path: str | None = None, update_after: int = 15, browser: str | None = None, login_timeout: int | None = None) -> None:
        if quotebook_path is None:
            res = files("quotescape.assets").joinpath("kindle_quotebook.json")
            with as_file(res) as p:
                self.quotebook_path = str(p)
        else:
            self.quotebook_path = quotebook_path

        self.url = "https://read.amazon.com/kp/notebook"

        self.default_timeout = 30  # seconds for typical Selenium waits
        self.update_after = update_after
        self.quotebook: dict[str, tuple[str, list[str]]] = {}
        # Browser preference: 'system' (detect default), specific ('chrome','firefox','edge','safari'), or 'auto' (fallback order)
        self.browser_pref = (browser or os.getenv("QUOTESCAPE_BROWSER") or "system").lower()
        # Login/2FA timeout in seconds
        try:
            env_timeout = int(os.getenv("QUOTESCAPE_LOGIN_TIMEOUT", "0"))
        except ValueError:
            env_timeout = 0
        self.login_timeout = login_timeout if login_timeout is not None else (env_timeout if env_timeout > 0 else 300)

    def importCredentials(self, secrets_path: str) -> tuple[str, str]:
        with open(secrets_path) as file:
            data = json.load(file)
            return data["username"], data["password"]

    def startSession(self):
        """Start a browser session using Selenium.

        Preference order:
        - If QUOTESCAPE_BROWSER env var or browser arg is provided, try that browser.
        - If 'system' on macOS, attempt to detect the default browser from LaunchServices.
        - Fallback order: Chrome -> Firefox -> Edge -> Safari (macOS only).
        """

        def _start_driver_for(name: str):
            name = name.lower()
            if name == "chrome":
                return webdriver.Chrome()
            if name == "firefox":
                return webdriver.Firefox()
            if name == "edge":
                return webdriver.Edge()
            if name == "safari":
                # Use SafariOptions when available to improve load behavior
                if SafariOptions is not None:
                    try:
                        opts = SafariOptions()
                        # Eager returns control sooner and avoids some stalls
                        # when Safari performs cross-domain redirects post-login
                        opts.page_load_strategy = "eager"  # type: ignore[attr-defined]
                        return webdriver.Safari(options=opts)
                    except Exception:
                        # Fallback to default constructor
                        return webdriver.Safari()
                else:
                    return webdriver.Safari()
            raise ValueError(f"Unsupported browser: {name}")

        def _detect_default_mac() -> str | None:
            try:
                plist_path = Path.home() / "Library" / "Preferences" / "com.apple.LaunchServices" / "com.apple.launchservices.secure.plist"
                if not plist_path.exists():
                    return None
                with plist_path.open('rb') as f:
                    data = plistlib.load(f)
                handlers = data.get("LSHandlers", [])
                for h in handlers:
                    if h.get("LSHandlerURLScheme") in ("http", "https"):
                        bundle_id = h.get("LSHandlerRoleAll")
                        if not bundle_id:
                            continue
                        mapping = {
                            "com.apple.Safari": "safari",
                            "com.google.Chrome": "chrome",
                            "org.mozilla.firefox": "firefox",
                            "com.microsoft.edgemac": "edge",
                        }
                        return mapping.get(bundle_id)
                return None
            except Exception:
                return None

        tried: list[str] = []

        # 1) Explicit preference via arg/env
        if self.browser_pref not in ("system", "auto"):
            try:
                self.driver = _start_driver_for(self.browser_pref)
                logger.info(f"Started browser via preference: {self.browser_pref}")
                return self.driver
            except Exception as e:
                tried.append(self.browser_pref)
                logger.debug(f"Failed to start preferred browser '{self.browser_pref}': {e}")

        # 2) System default (macOS)
        if platform.system() == "Darwin" and self.browser_pref == "system":
            detected = _detect_default_mac()
            if detected:
                try:
                    self.driver = _start_driver_for(detected)
                    logger.info(f"Started system default browser: {detected}")
                    return self.driver
                except Exception as e:
                    tried.append(detected)
                    logger.debug(f"Failed to start detected default browser '{detected}': {e}")

        # 3) Fallback order
        fallbacks = ["chrome", "firefox", "edge"]
        if platform.system() == "Darwin":
            fallbacks.append("safari")
        for b in fallbacks:
            if b in tried:
                continue
            try:
                self.driver = _start_driver_for(b)
                logger.info(f"Started browser via fallback: {b}")
                return self.driver
            except Exception as e:
                tried.append(b)
                logger.debug(f"Failed to start fallback browser '{b}': {e}")

        raise RuntimeError(
            "Could not start a browser. Tried: " + ", ".join(tried) + ". "
            "Ensure you have a supported browser installed. On Safari, enable 'Allow Remote Automation' in Develop menu."
        )

    def wait(self, element=None, locator: tuple | None = None) -> None:
        """Wait for either a given element object to display or a locator to appear."""
        if element is None and locator is None:
            self.driver.implicitly_wait(self.default_timeout)
            return
        selenium_wait = WebDriverWait(self.driver, timeout=self.default_timeout)
        if locator is not None:
            selenium_wait.until(EC.presence_of_element_located(locator))
        else:
            selenium_wait.until(lambda d: element.is_displayed())

    def wait_visible(self, locator: tuple, timeout: int | None = None):
        WebDriverWait(self.driver, timeout or self.default_timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_clickable(self, locator: tuple, timeout: int | None = None):
        WebDriverWait(self.driver, timeout or self.default_timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def _first_displayed(self, candidates: list):
        for el in candidates:
            try:
                if el.is_displayed() and el.is_enabled():
                    return el
            except Exception:
                continue
        return None

    def isOnNotebookPage(self) -> bool:
        """Detect Kindle Notebook page across variants.

        Handles both /kp/notebook and /notebook URLs and checks for key elements
        that exist on the page: library pane or annotations pane.
        """
        try:
            url = (self.driver.current_url or "").lower()
            if ("/kp/notebook" in url) or ("/notebook" in url):
                # Either the library panel or the annotations panel indicates we're there
                if self.driver.find_elements(By.ID, "kp-notebook-library"):
                    return True
                if self.driver.find_elements(By.ID, "kp-notebook-annotations"):
                    return True
                if self.driver.find_elements(By.ID, "annotations"):
                    return True
        except Exception:
            return False
        return False

    def isOnTwoFactorPage(self) -> bool:
        # Heuristics for Amazon 2FA flows
        selectors = [
            (By.ID, "auth-mfa-otpcode"),
            (By.NAME, "otpCode"),
            (By.ID, "auth-mfa-form"),
            (By.ID, "cvf-page-title"),
        ]
        for by, value in selectors:
            try:
                if self.driver.find_elements(by, value):
                    return True
            except Exception:
                continue
        try:
            elems = self.driver.find_elements(By.XPATH, "//h1[contains(., 'Two-Step Verification') or contains(., 'Verification code')]")
            if elems:
                return True
        except Exception:
            pass
        return False

    def waitForLoginCompletion(self, timeout: int | None = None) -> None:
        t = timeout if timeout is not None else self.login_timeout
        start = time.time()
        informed = False
        saw_2fa = False
        left_2fa_at: float | None = None
        grace_after_2fa = 25  # allow slower Safari redirects after 2FA
        attempted_redirect = False
        # Track window handles to catch Safari opening a new window after auth
        try:
            known_handles = set(self.driver.window_handles)
        except Exception:
            known_handles = set()

        while time.time() - start < t:
            # If a new window opens (Safari sometimes does this), switch to it
            try:
                handles = self.driver.window_handles
                for h in handles:
                    if h not in known_handles:
                        try:
                            self.driver.switch_to.window(h)
                            logger.debug("Switched to new browser window after login/2FA")
                        except Exception:
                            pass
                        known_handles.add(h)
            except Exception:
                pass

            # Success path: Notebook visible
            if self.isOnNotebookPage():
                return

            on_2fa = self.isOnTwoFactorPage()

            # Inform once when 2FA detected
            if on_2fa and not informed:
                logger.info("Two-Step Verification detected. Complete 2FA in the opened browser window. Waiting...")
                informed = True
                saw_2fa = True

            # If we previously saw 2FA and it is no longer showing, expect redirect to notebook shortly
            if saw_2fa and not on_2fa:
                if left_2fa_at is None:
                    left_2fa_at = time.time()
                else:
                    elapsed = time.time() - left_2fa_at
                    # One-time nudge: explicitly navigate to the notebook after a short wait
                    if not attempted_redirect and elapsed > 8:
                        try:
                            self.driver.get(self.url)
                            attempted_redirect = True
                            # Give the page a moment to load before re-checking
                            time.sleep(2)
                        except Exception:
                            pass
                    elif elapsed > grace_after_2fa:
                        # We left 2FA, but didn't land on the expected notebook page
                        raise RuntimeError(
                            "Unexpected post-2FA flow: did not reach Kindle Notebook. "
                            "2FA may have failed or additional verification is required."
                        )

            time.sleep(1.5)

        # Timeout handling with clearer context
        if saw_2fa:
            raise TimeoutError(
                "2FA/login did not complete within the allotted time. Finish verification or increase --login-timeout."
            )
        else:
            raise TimeoutError(
                "Login did not reach Kindle Notebook within the allotted time."
            )

    def login(self, secrets_path: str = "settings/secrets.json") -> None:
        username, password = self.importCredentials(secrets_path)
        self.driver.get(self.url)

        # Email step
        # Wait for either name=email or id=ap_email to be visible
        try:
            self.wait_visible((By.NAME, "email"))
        except TimeoutException:
            try:
                self.wait_visible((By.ID, "ap_email"))
            except TimeoutException:
                pass

        email_candidates = []
        try:
            email_candidates.extend(self.driver.find_elements(By.NAME, "email"))
        except Exception:
            pass
        try:
            email_candidates.extend(self.driver.find_elements(By.ID, "ap_email"))
        except Exception:
            pass
        username_box = self._first_displayed(email_candidates)
        if not username_box:
            raise TimeoutException("Email input not found or not interactable")

        # Continue button clickable
        self.wait_clickable((By.ID, "continue"))
        username_box.clear()
        username_box.send_keys(username)
        self.driver.find_element(By.ID, "continue").click()

        # Password step (if presented). If we're already on Notebook or 2FA, skip.
        try:
            if self.isOnNotebookPage() or self.isOnTwoFactorPage():
                raise TimeoutException("Skipping password step; already on Notebook or 2FA page")
            try:
                self.wait_visible((By.NAME, "password"), timeout=10)
            except TimeoutException:
                self.wait_visible((By.ID, "ap_password"), timeout=10)

            # Helper to (re)locate and set the password, resilient to stale elements
            def _set_password(value: str) -> bool:
                try:
                    # If 2FA already showed up, stop trying to type password
                    if self.isOnTwoFactorPage():
                        return True
                except Exception:
                    pass
                candidates = []
                try:
                    candidates.extend(self.driver.find_elements(By.NAME, "password"))
                except Exception:
                    pass
                try:
                    candidates.extend(self.driver.find_elements(By.ID, "ap_password"))
                except Exception:
                    pass
                box = self._first_displayed(candidates)
                if not box:
                    return False
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", box)
                except Exception:
                    pass
                try:
                    box.click()
                except Exception:
                    pass
                try:
                    # Avoid clear(); on Safari this often stales during page morphs
                    box.send_keys(value)
                    return True
                except StaleElementReferenceException:
                    return False
                except Exception:
                    # JS fallback: query element fresh within the page and set value
                    try:
                        ok = self.driver.execute_script(
                            'var el=document.getElementById("ap_password")||document.querySelector(\'input[name="password"]\'); if(el){el.value=arguments[0]; return true;} return false;',
                            value,
                        )
                        return bool(ok)
                    except Exception:
                        return False

            # Try a few times in case Safari swaps the DOM beneath us
            attempts = 0
            while attempts < 3:
                if _set_password(password):
                    break
                attempts += 1
                time.sleep(0.5)

            # Click sign in if available (ignore if the flow has moved on)
            try:
                if not (self.isOnNotebookPage() or self.isOnTwoFactorPage()):
                    self.wait_clickable((By.ID, "signInSubmit"))
                    self.driver.find_element(By.ID, "signInSubmit").click()
            except TimeoutException:
                pass
            except StaleElementReferenceException:
                # Likely navigated; proceed to wait phase
                pass
        except TimeoutException:
            # Possibly redirected into a different flow (e.g., 2FA or captcha)
            pass

        # Wait until login completes or user finishes 2FA
        self.waitForLoginCompletion()

    def stopSession(self) -> None:
        self.driver.close()
        self.driver.quit()

    def isQuotebookOutdated(self, quotebook_path) -> bool:
        quotebook_modified_time = path.getmtime(quotebook_path)
        cutoff = datetime.utcnow() - timedelta(days=self.update_after)
        return datetime.utcfromtimestamp(quotebook_modified_time) < cutoff

    def importLocalQuotebook(self, quotebook_path):
        if not path.exists(quotebook_path) or self.isQuotebookOutdated(quotebook_path):
            self.updateLocalQuotebook()
        with open(quotebook_path) as file:
            self.quotebook = json.load(file)
            return self.quotebook

    def getTitleCoverAndQuotes(self) -> tuple[str, list[str]]:
        self.wait(locator=(By.ID, "kp-notebook-annotations"))
        annotations = self.driver.find_element(By.ID, "kp-notebook-annotations")
        quotes = annotations.find_elements(By.ID, "highlight")
        annotations_pane = self.driver.find_element(By.ID, "annotations")
        cover_url = annotations_pane.find_element(
            By.CLASS_NAME, "kp-notebook-cover-image-border").get_attribute("src")
        if cover_url is not None:
            cover_url = cover_url.replace("_SY160", "_SY2400")
        else:
            cover_url = ""
        quotes_list: list[str] = []
        for quote in quotes:
            if len(quote.text) != 0:
                quotes_list.append(quote.text)
        return (cover_url, quotes_list)

    def buildQuotebook(self) -> None:
        # Wait for library to populate
        self.wait(locator=(By.ID, "kp-notebook-library"))
        library = self.driver.find_element(By.ID, "kp-notebook-library")
        # Prefer specific book entries if available
        entries = []
        try:
            entries = library.find_elements(By.CLASS_NAME, "kp-notebook-library-each-book")
        except Exception:
            pass
        if not entries:
            # Fallback to clickable divs with text
            entries = [el for el in library.find_elements(By.TAG_NAME, "div") if el.text.strip()]

        for book in entries:
            raw_label = book.text.strip()
            key = self._normalize_book_label(raw_label)
            if not key:
                continue
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", book)
            except Exception:
                pass
            try:
                book.click()
            except Exception:
                # Fallback JS click
                try:
                    self.driver.execute_script("arguments[0].click();", book)
                except Exception:
                    continue
            self.wait()
            cover_url, quotes = self.getTitleCoverAndQuotes()
            self.quotebook.update({key: (cover_url, quotes)})

    def updateLocalQuotebook(self) -> None:
        self.startSession()
        try:
            self.login()
            self.buildQuotebook()
        finally:
            self.stopSession()
        with open(self.quotebook_path, "w") as quotebook_file:
            json.dump(self.quotebook, quotebook_file, indent=4)

    def _normalize_book_label(self, raw: str) -> str:
        """Return 'Title\nBy: Author' only if 'By:' is present; else return title only.

        This enforces the strict, newline-delimited format in the stored JSON.
        """
        raw = raw.strip()
        if "\n" in raw:
            return raw
        idx = raw.find("By:")
        if idx != -1:
            title = raw[:idx].strip()
            author = raw[idx + len("By:"):].strip()
            if title and author:
                return f"{title}\nBy: {author}"
        return raw

    def _parse_title_author(self, raw: str) -> tuple[str, str | None]:
        """Extract (book, author) from a label strictly formatted as:
        'Title\nBy: Author'. If not in this format, return (title, None).
        """
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        if len(lines) >= 2 and lines[1].startswith("By: "):
            book = lines[0]
            author = lines[1][4:].strip()
            return book, author or None
        return (lines[0] if lines else raw.strip()), None

    def getRandom(self) -> tuple[str, str, str | None, str]:
        logger.debug("hit getRandom")
        if not self.quotebook:
            self.importLocalQuotebook(quotebook_path=self.quotebook_path)
        # Filter to entries that have at least one quote
        viable = [(k, v) for k, v in self.quotebook.items() if isinstance(v, (list, tuple)) and v and v[1]]
        if not viable:
            raise ValueError("No quotes found in Kindle quotebook cache.")
        title, data = random.choice(viable)
        cover_url = data[0]
        quotes_list = data[1]
        quote = random.choice(quotes_list)
        book, author = self._parse_title_author(title)
        return quote, book, author, cover_url


def main():
    print(KindleQuotes().getRandom())


if __name__ == "__main__":
    main()

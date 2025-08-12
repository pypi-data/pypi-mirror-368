"""
Jarvis Speech-to-Text Selenium bridge (package-ready)

Features:
- Launches the packaged frontend (index.html) via Selenium + Chrome
- Polls the DOM for recognized speech (#outputText)
- Reads the translation toggle state (#translationToggle.checked)
- If translation toggle is ON, translates text to English using `mtranslate.translate`
- Writes processed result to an output file (default: input.txt)
- Suppresses many Chrome/Chromium noisy logs
"""

from pathlib import Path
import time
import sys
import traceback

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Optional translation library
try:
    from mtranslate import translate as mtranslate_translate
    _HAS_MTRANSLATE = True
except Exception:
    _HAS_MTRANSLATE = False


def _get_driver(headless: bool = False, allow_fake_media: bool = True):
    """Create a Chrome WebDriver with noise suppressed and optional headless mode."""
    options = webdriver.ChromeOptions()

    # Allow mic auto-approve for automated testing (use with caution)
    if allow_fake_media:
        options.add_argument("--use-fake-ui-for-media-stream")

    # Recommended for packaging/test usage: do not run headless when accessing microphone.
    if headless:
        options.add_argument("--headless=new")

    # Useful flags to reduce noisy logging
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Create WebDriver (auto-installs driver)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def _get_index_url(package_dir: Path, server_mode: bool):
    """Return a URL to open: either file:// or http://localhost:8000/index.html if server_mode."""
    index_path = package_dir / "index.html"
    if server_mode:
        # Assumes user started a local HTTP server serving package_dir at port 8000
        return f"http://localhost:8000/{index_path.name}"
    else:
        return f"file:///{index_path}"


def listen(
    output_file: str = None,
    headless: bool = False,
    allow_fake_media: bool = True,
    server_mode: bool = False,
    pack_dir: str = None,
    poll_interval: float = 0.8,
):
    """
    Launch the packaged frontend and stream recognized speech to `output_file`.

    Args:
        output_file (str): Path to save processed text. If None, prints to stdout.
        headless (bool): Run Chrome headless (not recommended for real microphone use).
        allow_fake_media (bool): Adds Chrome flag to auto-allow mic (for tests).
        server_mode (bool): If True, will open http://localhost:8000/index.html (requires a http.server).
        pack_dir (str): Directory where package files reside (defaults to this module's dir).
        poll_interval (float): Seconds between polls of the DOM.
    """
    pkg_dir = Path(pack_dir) if pack_dir else Path(__file__).resolve().parent
    index_file = pkg_dir / "index.html"

    if not index_file.exists():
        raise FileNotFoundError(f"index.html not found in package directory: {pkg_dir}")

    driver = None
    try:
        driver = _get_driver(headless=headless, allow_fake_media=allow_fake_media)
        url = _get_index_url(pkg_dir, server_mode=server_mode)
        driver.get(url)

        # Wait for the UI controls to appear
        wait = WebDriverWait(driver, 15)
        start_btn = wait.until(EC.element_to_be_clickable((By.ID, "startButton")))
        print("[Jarvis] 🎤 Found UI — starting listening.")
        start_btn.click()

        last_text = ""
        out_path = Path(output_file) if output_file else None

        print("[Jarvis] Listening... Press Ctrl+C to stop.")
        while True:
            try:
                # get the raw transcript element
                out_el = driver.find_element(By.ID, "outputText")
                raw_text = out_el.text.strip()

                # get the translation toggle state (checkbox checked boolean)
                # we use JS to avoid cross-browser issues
                try:
                    toggle_state = driver.execute_script(
                        "const el=document.getElementById('translationToggle'); return el ? !!el.checked : false;"
                    )
                except Exception:
                    toggle_state = False

                # If empty or unchanged, skip
                if not raw_text or raw_text == last_text:
                    time.sleep(poll_interval)
                    continue

                last_text = raw_text

                # Perform backend translation if toggle enabled
                processed = raw_text
                if toggle_state:
                    if _HAS_MTRANSLATE:
                        try:
                            # translate to English
                            processed = mtranslate_translate(raw_text, 'en')
                        except Exception:
                            # fallback to raw if translation fails
                            processed = raw_text
                    else:
                        # mtranslate not available
                        processed = raw_text
                        print("[Jarvis] Warning: 'mtranslate' not installed. Install with `pip install mtranslate` for backend translation.")

                # Save or print processed result
                if out_path:
                    try:
                        out_path.write_text(processed, encoding="utf-8")
                    except Exception as e:
                        print(f"[Jarvis] Error writing to {out_path}: {e}")
                else:
                    print("[Processed]:", processed)

            except KeyboardInterrupt:
                print("\n[Jarvis] Stopping by user (KeyboardInterrupt).")
                break
            except Exception:
                # Print stack trace once and continue polling
                traceback.print_exc()
                time.sleep(poll_interval)
                continue

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        print("[Jarvis] Listener terminated.")


if __name__ == "__main__":
    # Quick test when running as script from package folder.
    # It will write to input.txt in current working directory.
    try:
        listen(output_file="input.txt", headless=False, allow_fake_media=True, server_mode=False)
    except Exception as ex:
        print("Error launching listener:", ex)
        sys.exit(1)

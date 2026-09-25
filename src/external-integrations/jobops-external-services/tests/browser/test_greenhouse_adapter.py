import os
from pathlib import Path

from playwright.sync_api import sync_playwright

from source.externalService.ats.GreenhouseATSAdapter import (
    GreenhouseATSAdapter,
)
from source.service.CandidateProfileService import (
    CandidateProfileService,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURE = FIXTURE_DIR / "greenhouse_form.html"
CAPTCHA_FIXTURE = FIXTURE_DIR / "captcha_form.html"
RESUME_FIXTURE = FIXTURE_DIR / "resume.pdf"


def _browser(playwright):
    executable = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    if executable:
        return playwright.chromium.launch(
            headless=True,
            executable_path=executable,
        )
    if Path("/usr/bin/chromium").exists():
        return playwright.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
        )
    return playwright.chromium.launch(headless=True)


def test_greenhouse_dry_run_fills_known_fields_and_never_submits(
    tmp_path,
):
    profile = CandidateProfileService.get_profile()
    adapter = GreenhouseATSAdapter(
        profile,
        RESUME_FIXTURE,
    )
    with sync_playwright() as playwright:
        browser = _browser(playwright)
        page = browser.new_page()
        page.set_content(
            FIXTURE.read_text(encoding="utf-8")
        )
        result = adapter.fill_page(page)
        screenshot_path = tmp_path / "filled.png"
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        assert (
            page.locator("#first_name").input_value()
            == "Jordan"
        )
        assert (
            page.locator("#last_name").input_value()
            == "Lee"
        )
        assert (
            page.locator("#email").input_value()
            == "jordan@example.com"
        )
        assert result.resume_uploaded is True
        assert result.submit_clicked is False
        assert any(
            "Expected salary" in value
            for value in result.protected_fields
        )
        assert any(
            "Why do you want to work here" in value
            for value in result.missing_fields
        )
        assert result.status == "NEEDS_INPUT"
        assert any(
            field.status == "filled"
            for field in result.fields
        )
        assert screenshot_path.exists()
        browser.close()


def test_greenhouse_dry_run_stops_on_captcha():
    profile = CandidateProfileService.get_profile()
    adapter = GreenhouseATSAdapter(
        profile,
        RESUME_FIXTURE,
    )
    with sync_playwright() as playwright:
        browser = _browser(playwright)
        page = browser.new_page()
        page.set_content(
            CAPTCHA_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
        result = adapter.fill_page(page)
        assert result.status == "HUMAN_ACTION_REQUIRED"
        assert result.captcha_detected is True
        assert result.submit_clicked is False
        browser.close()


def test_greenhouse_artifact_writer_persists_trace_and_screenshot(
    tmp_path,
):
    profile = CandidateProfileService.get_profile()
    adapter = GreenhouseATSAdapter(
        profile,
        RESUME_FIXTURE,
    )
    with sync_playwright() as playwright:
        browser = _browser(playwright)
        page = browser.new_page()
        page.set_content(
            FIXTURE.read_text(encoding="utf-8")
        )
        result = adapter.fill_page(page)
        result = adapter._persist_artifacts(
            page,
            result,
            tmp_path,
        )
        browser.close()

    assert result.submit_clicked is False
    assert result.screenshot_path is not None
    assert result.result_path is not None
    assert Path(result.screenshot_path).exists()
    assert Path(result.result_path).exists()
    assert any(
        event.step == "submit_gate"
        for event in result.trace
    )


def test_greenhouse_rejects_non_greenhouse_target():
    profile = CandidateProfileService.get_profile()
    adapter = GreenhouseATSAdapter(
        profile,
        RESUME_FIXTURE,
    )
    try:
        adapter._validate_target_url(
            "http://127.0.0.1:8000/internal"
        )
    except ValueError as exc:
        assert "greenhouse.io" in str(exc)
    else:
        raise AssertionError(
            "Expected non-Greenhouse URL to be rejected"
        )

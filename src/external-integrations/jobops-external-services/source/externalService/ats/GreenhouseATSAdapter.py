from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import Page, sync_playwright

from source.externalService.ats.BaseATSAdapter import ATSAdapter
from source.schemas.ApplicationSchemas import (
    ApplicationFieldResult,
    BrowserTraceEvent,
    DryRunResult,
)
from source.service.ApplicationFieldResolverService import ApplicationFieldResolverService


class GreenhouseATSAdapter(ATSAdapter):
    ats_type = "greenhouse"

    def __init__(self, profile: dict, resume_path: str | Path):
        super().__init__(profile, resume_path)
        self.resolver = ApplicationFieldResolverService(profile)
        self.trace: list[BrowserTraceEvent] = []
        self.fields: list[ApplicationFieldResult] = []

    def _event(self, step: str, status: str, detail: str) -> None:
        self.trace.append(BrowserTraceEvent(step=step, status=status, detail=detail))

    def _field(
        self,
        descriptor: str,
        field_type: str,
        status: str,
        value_source: str | None = None,
    ) -> None:
        self.fields.append(
            ApplicationFieldResult(
                descriptor=descriptor,
                field_type=field_type,
                status=status,
                value_source=value_source,
            )
        )

    @staticmethod
    def _validate_target_url(url: str) -> None:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Greenhouse dry-run only supports http/https URLs")
        if host != "greenhouse.io" and not host.endswith(".greenhouse.io"):
            raise ValueError(
                "Greenhouse adapter only accepts greenhouse.io application URLs"
            )

    def _detect_captcha(self, page: Page) -> bool:
        body = self.resolver.normalize(page.locator("body").inner_text())
        iframe_count = page.locator(
            'iframe[src*="recaptcha"], iframe[src*="hcaptcha"]'
        ).count()
        return "captcha" in body or iframe_count > 0

    def _descriptor(self, page: Page, control) -> str:
        control_id = control.get_attribute("id")
        name = control.get_attribute("name") or ""
        aria = control.get_attribute("aria-label") or ""
        placeholder = control.get_attribute("placeholder") or ""
        label = ""
        if control_id:
            label_locator = page.locator(f'label[for="{control_id}"]')
            if label_locator.count():
                label = label_locator.first.inner_text().strip()
        return " ".join(
            value for value in [label, aria, placeholder, name] if value
        ).strip()

    def fill_page(self, page: Page) -> DryRunResult:
        self.trace = []
        self.fields = []
        filled: list[str] = []
        missing: list[str] = []
        protected: list[str] = []
        resume_uploaded = False

        self._event("open", "ok", f"Opened {page.url}")
        if self._detect_captcha(page):
            self._event(
                "captcha",
                "blocked",
                "CAPTCHA detected; human action required",
            )
            return DryRunResult(
                status="HUMAN_ACTION_REQUIRED",
                ats_type=self.ats_type,
                filled_fields=filled,
                missing_fields=missing,
                protected_fields=protected,
                resume_uploaded=False,
                captcha_detected=True,
                submit_clicked=False,
                trace=self.trace,
                fields=self.fields,
            )

        controls = page.locator("input, textarea, select")
        count = controls.count()
        self._event("scan_fields", "ok", f"Found {count} form controls")

        for index in range(count):
            control = controls.nth(index)
            if not control.is_visible():
                continue
            control_type = (control.get_attribute("type") or "").lower()
            tag = control.evaluate("el => el.tagName.toLowerCase()")
            if control_type in {"hidden", "submit", "button"}:
                continue

            descriptor = self._descriptor(page, control) or f"field_{index}"
            normalized = self.resolver.normalize(descriptor)
            field_type = control_type or tag

            if (
                control_type == "file"
                or "resume" in normalized
                or "cv" in normalized
            ):
                if self.resume_path.exists():
                    control.set_input_files(str(self.resume_path))
                    resume_uploaded = True
                    filled.append(descriptor)
                    self._field(descriptor, field_type, "filled", "resume")
                    self._event("upload_resume", "ok", self.resume_path.name)
                else:
                    missing.append(descriptor)
                    self._field(descriptor, field_type, "missing")
                    self._event("upload_resume", "error", "Resume file missing")
                continue

            protected_kind = self.resolver.classify_protected(descriptor)
            if protected_kind:
                protected.append(descriptor)
                self._field(
                    descriptor,
                    field_type,
                    "protected",
                    protected_kind,
                )
                self._event("protected_field", "blocked", descriptor)
                continue

            if control_type in {"checkbox", "radio"} or tag == "select":
                missing.append(descriptor)
                self._field(descriptor, field_type, "needs_review")
                self._event("choice_field", "needs_review", descriptor)
                continue

            value = self.resolver.known_value(descriptor)
            if value:
                control.fill(value)
                filled.append(descriptor)
                self._field(
                    descriptor,
                    field_type,
                    "filled",
                    "candidate_profile",
                )
                self._event("fill_field", "ok", descriptor)
            else:
                missing.append(descriptor)
                self._field(descriptor, field_type, "missing")
                self._event("unknown_field", "needs_review", descriptor)

        status = "NEEDS_INPUT" if protected or missing else "READY_FOR_REVIEW"
        self._event(
            "submit_gate",
            "stopped",
            "Dry run completed; submit was not clicked",
        )
        return DryRunResult(
            status=status,
            ats_type=self.ats_type,
            filled_fields=filled,
            missing_fields=missing,
            protected_fields=protected,
            resume_uploaded=resume_uploaded,
            captcha_detected=False,
            submit_clicked=False,
            trace=self.trace,
            fields=self.fields,
        )

    def _persist_artifacts(
        self,
        page: Page,
        result: DryRunResult,
        artifact_dir: str | Path,
    ) -> DryRunResult:
        artifact_root = Path(artifact_dir)
        artifact_root.mkdir(parents=True, exist_ok=True)
        screenshot_path = artifact_root / "filled-form.png"
        result_path = artifact_root / "dry-run.json"
        page.screenshot(path=str(screenshot_path), full_page=True)
        result.screenshot_path = str(screenshot_path)
        result.result_path = str(result_path)
        result_path.write_text(
            result.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return result

    def run_dry_run(
        self,
        url: str,
        artifact_dir: str | None = None,
    ) -> DryRunResult:
        self._validate_target_url(url)
        with sync_playwright() as playwright:
            executable = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
            if not executable and Path("/usr/bin/chromium").exists():
                executable = "/usr/bin/chromium"
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=executable,
            )
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            result = self.fill_page(page)
            if artifact_dir:
                result = self._persist_artifacts(
                    page,
                    result,
                    artifact_dir,
                )
            browser.close()
            return result

"""Stage 23 -- services/integration/notifier.py, the real SMTP sender.

Deliberately narrow: this module's only two jobs are "refuse cleanly when not
configured" and "send correctly when it is," so those are the only two things tested.
Nothing here calls a real Gmail server -- smtplib.SMTP/SMTP_SSL are faked so the tests
never depend on network access or real credentials, and can still assert exactly what
would have been sent (recipient, STARTTLS, login).
"""
from __future__ import annotations

import pytest

from services.integration import notifier


@pytest.fixture(autouse=True)
def _clear_smtp_env(monkeypatch):
    for var in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "NOTIFY_EMAIL_TO"):
        monkeypatch.delenv(var, raising=False)


def test_raises_a_clear_error_when_nothing_is_configured():
    with pytest.raises(notifier.EmailNotConfigured, match="SMTP_HOST"):
        notifier.send_email("subject", "body")


def test_lists_every_missing_variable_not_just_the_first(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    with pytest.raises(notifier.EmailNotConfigured) as exc:
        notifier.send_email("subject", "body")
    assert "SMTP_USER" in str(exc.value)
    assert "SMTP_PASSWORD" in str(exc.value)
    assert "recipient" in str(exc.value)


def test_recipient_can_come_from_notify_email_to_or_be_overridden(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_USER", "aegis@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password")
    # Neither NOTIFY_EMAIL_TO nor an explicit `to` -- still not configured.
    with pytest.raises(notifier.EmailNotConfigured, match="recipient"):
        notifier.send_email("subject", "body")


class _FakeSMTP:
    instances: list["_FakeSMTP"] = []

    def __init__(self, host, port, timeout=10):
        self.host, self.port = host, port
        self.started_tls = False
        self.logged_in = None
        self.sent = None
        _FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, user, password):
        self.logged_in = (user, password)

    def send_message(self, message):
        self.sent = message


@pytest.fixture(autouse=True)
def _reset_fake_smtp():
    _FakeSMTP.instances.clear()
    yield
    _FakeSMTP.instances.clear()


def _configure(monkeypatch, **overrides):
    env = {
        "SMTP_HOST": "smtp.gmail.com", "SMTP_PORT": "587",
        "SMTP_USER": "aegis@example.com", "SMTP_PASSWORD": "app-password",
        "NOTIFY_EMAIL_TO": "puranam.dinesh@gmail.com",
    }
    env.update(overrides)
    for key, value in env.items():
        monkeypatch.setenv(key, value)


def test_sends_over_starttls_on_the_default_port(monkeypatch):
    _configure(monkeypatch)
    monkeypatch.setattr(notifier.smtplib, "SMTP", _FakeSMTP)

    notifier.send_email("Escalation", "A run needs attention.")

    assert len(_FakeSMTP.instances) == 1
    smtp = _FakeSMTP.instances[0]
    assert smtp.host == "smtp.gmail.com"
    assert smtp.started_tls is True
    assert smtp.logged_in == ("aegis@example.com", "app-password")
    assert smtp.sent["To"] == "puranam.dinesh@gmail.com"
    assert smtp.sent["Subject"] == "Escalation"
    assert smtp.sent.get_content().strip() == "A run needs attention."


def test_uses_smtp_ssl_on_port_465_without_starttls(monkeypatch):
    _configure(monkeypatch, SMTP_PORT="465")
    monkeypatch.setattr(notifier.smtplib, "SMTP_SSL", _FakeSMTP)

    notifier.send_email("Escalation", "A run needs attention.")

    assert len(_FakeSMTP.instances) == 1
    assert _FakeSMTP.instances[0].started_tls is False  # SMTP_SSL never calls starttls
    assert _FakeSMTP.instances[0].logged_in == ("aegis@example.com", "app-password")


def test_an_explicit_recipient_overrides_notify_email_to(monkeypatch):
    _configure(monkeypatch)
    monkeypatch.setattr(notifier.smtplib, "SMTP", _FakeSMTP)

    notifier.send_email("Subject", "Body", to="someone-else@example.com")

    assert _FakeSMTP.instances[0].sent["To"] == "someone-else@example.com"


def test_smtp_from_defaults_to_smtp_user(monkeypatch):
    _configure(monkeypatch)
    monkeypatch.setattr(notifier.smtplib, "SMTP", _FakeSMTP)

    notifier.send_email("Subject", "Body")

    assert _FakeSMTP.instances[0].sent["From"] == "aegis@example.com"


def test_smtp_from_can_be_set_separately(monkeypatch):
    _configure(monkeypatch, SMTP_FROM="notifications@example.com")
    monkeypatch.setattr(notifier.smtplib, "SMTP", _FakeSMTP)

    notifier.send_email("Subject", "Body")

    assert _FakeSMTP.instances[0].sent["From"] == "notifications@example.com"


def test_an_invalid_port_is_reported_as_not_configured_not_a_crash(monkeypatch):
    _configure(monkeypatch, SMTP_PORT="not-a-number")
    with pytest.raises(notifier.EmailNotConfigured, match="SMTP_PORT"):
        notifier.send_email("Subject", "Body")

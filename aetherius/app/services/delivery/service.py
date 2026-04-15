import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session
from weasyprint import HTML

from app.core.config import settings
from app.models.entities import BriefingEvidenceRefs, BriefingItems, BriefingRuns, Deliveries


def _env() -> Environment:
    template_dir = Path(__file__).resolve().parents[2] / "templates"
    return Environment(loader=FileSystemLoader(str(template_dir)), autoescape=select_autoescape(["html"]))


def render_email(briefing_run: BriefingRuns, items: list[BriefingItems]) -> str:
    template = _env().get_template("email/daily_brief.html")
    return template.render(run=briefing_run, items=items)


def render_pdf_html(briefing_run: BriefingRuns, items: list[BriefingItems]) -> str:
    template = _env().get_template("pdf/daily_brief.html")
    return template.render(run=briefing_run, items=items)


def render_pdf_bytes(briefing_run: BriefingRuns, items: list[BriefingItems]) -> bytes:
    html = render_pdf_html(briefing_run, items)
    return HTML(string=html).write_pdf()


def quality_gates(items: list[BriefingItems], recipient: str) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not items:
        issues.append("No briefing items to send.")
    if "@" not in recipient:
        issues.append("Recipient is invalid.")
    for item in items:
        if item.severity_level in {"elevated", "high"} and not item.body:
            issues.append(f"Missing explanation body for elevated/high item: {item.title}")
        banned = ["guaranteed", "certain", "must", "obvious crash"]
        body = (item.body or "").lower()
        if any(w in body for w in banned):
            issues.append(f"Forbidden language in item: {item.title}")
    return (len(issues) == 0, issues)


def send_email(recipient: str, subject: str, html_body: str) -> str:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.smtp_from, [recipient], msg.as_string())
    return f"smtp-{datetime.utcnow().timestamp()}"


def deliver_briefing(db: Session, briefing_run_id: str, recipient: str, channel: str = "email") -> Deliveries:
    run = db.query(BriefingRuns).filter(BriefingRuns.id == briefing_run_id).one()
    items = db.query(BriefingItems).filter(BriefingItems.briefing_run_id == briefing_run_id).order_by(BriefingItems.display_order).all()
    ok, issues = quality_gates(items, recipient)
    delivery = Deliveries(
        briefing_run_id=briefing_run_id,
        channel=channel,
        recipient=recipient,
        delivery_status="queued",
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    if not ok:
        delivery.delivery_status = "failed"
        delivery.error_message = "; ".join(issues)
        delivery.attempt_count = delivery.attempt_count + 1
        delivery.last_attempt_at = datetime.utcnow()
        db.commit()
        return delivery
    duplicate_recent = (
        db.query(Deliveries)
        .filter(
            Deliveries.briefing_run_id == briefing_run_id,
            Deliveries.recipient == recipient,
            Deliveries.delivery_status == "sent",
        )
        .first()
    )
    if duplicate_recent:
        delivery.delivery_status = "failed"
        delivery.error_message = "Duplicate alert suppressed unless materially changed."
        delivery.attempt_count = delivery.attempt_count + 1
        delivery.last_attempt_at = datetime.utcnow()
        db.commit()
        return delivery

    high_items = [i for i in items if i.severity_level in {"elevated", "high"}]
    for hi in high_items:
        has_ref = db.query(BriefingEvidenceRefs).filter(BriefingEvidenceRefs.briefing_item_id == hi.id).count() > 0
        if not has_ref:
            delivery.delivery_status = "failed"
            delivery.error_message = f"Missing evidence for high severity item: {hi.title}"
            delivery.attempt_count = delivery.attempt_count + 1
            delivery.last_attempt_at = datetime.utcnow()
            db.commit()
            return delivery

    try:
        html = render_email(run, items)
        # Render PDF to enforce render-success quality gate.
        _ = render_pdf_bytes(run, items)
        message_id = send_email(recipient, f"Aetherius Brief - {run.run_type}", html)
        delivery.delivery_status = "sent"
        delivery.provider_message_id = message_id
        delivery.attempt_count = delivery.attempt_count + 1
        delivery.last_attempt_at = datetime.utcnow()
        run.status = "sent"
        run.sent_at = datetime.utcnow()
    except Exception as exc:
        delivery.delivery_status = "failed"
        delivery.error_message = str(exc)
        delivery.attempt_count = delivery.attempt_count + 1
        delivery.last_attempt_at = datetime.utcnow()
    db.commit()
    db.refresh(delivery)
    return delivery


def retry_failed_delivery(db: Session, delivery_id: str, max_attempts: int = 3) -> Deliveries:
    delivery = db.query(Deliveries).filter(Deliveries.id == delivery_id).one()
    if delivery.delivery_status != "failed" or delivery.attempt_count >= max_attempts:
        return delivery
    wait_factor = 2 ** max(delivery.attempt_count - 1, 0)
    delivery.error_message = f"retry_scheduled_backoff_factor={wait_factor}"
    delivery.delivery_status = "queued"
    db.commit()
    return delivery

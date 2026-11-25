import logging
from openai import OpenAI

client = OpenAI()
log = logging.getLogger(__name__)


def summarize_invoice(invoice_text: str, customer_email: str) -> str:
    log.info("summarizing for %s: %s", customer_email, invoice_text)
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Summarize this invoice:\n{invoice_text}"}],
        )
    except Exception:
        # fall back to a cheaper model
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Summarize this invoice:\n{invoice_text}"}],
        )
    return resp.choices[0].message.content

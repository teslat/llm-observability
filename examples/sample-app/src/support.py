import anthropic

claude = anthropic.Anthropic()

SUPPORT_PROMPT_V3 = "You are a support agent for {tenant_name}. Answer briefly."


def answer_ticket(tenant_id: str, tenant_name: str, question: str) -> str:
    msg = claude.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=SUPPORT_PROMPT_V3.format(tenant_name=tenant_name),
        messages=[{"role": "user", "content": question}],
    )
    return msg.content[0].text

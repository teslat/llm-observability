# Python wrapper template

One span per LLM call. Adapt the client call (`llm(...)`) and response fields to the project's SDK. `redact_pii` is the project's own redaction function; create one if none exists.

```python
# pip install opentelemetry-sdk opentelemetry-exporter-otlp
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import Status, StatusCode

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("llm-app")

def call_llm(llm, messages, *, model, feature, tenant_id, prompt_version):
    with tracer.start_as_current_span(f"chat {model}") as span:
        span.set_attributes({
            "gen_ai.operation.name": "chat",
            "gen_ai.provider.name": "openai",
            "gen_ai.request.model": model,
            "app.feature": feature,
            "app.tenant_id": tenant_id,
            "app.prompt_version": prompt_version,
        })
        try:
            resp = llm(model=model, messages=redact_pii(messages))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR))
            span.set_attribute("app.outcome", "error")
            raise
        span.set_attributes({
            "gen_ai.response.model": resp.model,
            "gen_ai.usage.input_tokens": resp.input_tokens,
            "gen_ai.usage.output_tokens": resp.output_tokens,
            "app.outcome": "success",
        })
        return resp
```

Endpoint and service name come from `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_SERVICE_NAME`. If the project already configures a TracerProvider, reuse it and skip the setup lines.

Add `app.fallback_used`, `app.guardrail`, `app.business_event_id` and `app.cost_usd` where the project has that information.

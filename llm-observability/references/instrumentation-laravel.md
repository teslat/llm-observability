# PHP / Laravel wrapper template

Bind `TracedLlm` in a service provider and route every call through it. `LlmClient` and `Redactor::pii` stand for the project's own client and redaction code.

```php
// composer require open-telemetry/sdk open-telemetry/exporter-otlp
// plus a PSR-18 HTTP client. In .env: OTEL_PHP_AUTOLOAD_ENABLED=true,
// OTEL_SERVICE_NAME, OTEL_EXPORTER_OTLP_ENDPOINT.
use OpenTelemetry\API\Globals;
use OpenTelemetry\API\Trace\SpanKind;
use OpenTelemetry\API\Trace\StatusCode;

final class TracedLlm
{
    public function __construct(private LlmClient $client) {}

    public function chat(array $messages, string $model, string $feature,
                         string $tenantId, string $promptVersion): array
    {
        $span = Globals::tracerProvider()->getTracer('llm-app')
            ->spanBuilder("chat {$model}")
            ->setSpanKind(SpanKind::KIND_CLIENT)
            ->startSpan();
        $scope = $span->activate();
        try {
            $span->setAttributes([
                'gen_ai.operation.name' => 'chat',
                'gen_ai.provider.name'  => 'openai',
                'gen_ai.request.model'  => $model,
                'app.feature'           => $feature,
                'app.tenant_id'         => $tenantId,
                'app.prompt_version'    => $promptVersion,
            ]);
            $resp = $this->client->chat($model, Redactor::pii($messages));
            $span->setAttributes([
                'gen_ai.response.model'      => $resp['model'],
                'gen_ai.usage.input_tokens'  => $resp['input_tokens'],
                'gen_ai.usage.output_tokens' => $resp['output_tokens'],
                'app.outcome'                => 'success',
            ]);
            return $resp;
        } catch (\Throwable $e) {
            $span->recordException($e);
            $span->setStatus(StatusCode::STATUS_ERROR);
            $span->setAttribute('app.outcome', 'error');
            throw $e;
        } finally {
            $scope->detach();
            $span->end();
        }
    }
}
```

Check package versions against the OpenTelemetry PHP docs. With Laravel, set the `OTEL_*` variables in `.env` and make sure they reach the queue workers too, not only the web process.

<?php

namespace App\Services;

use OpenAI\Laravel\Facades\OpenAI;

class InvoiceAssistant
{
    public function explain(string $tenantId, string $question): string
    {
        $result = OpenAI::chat()->create([
            'model' => 'gpt-4o-mini',
            'messages' => [['role' => 'user', 'content' => $question]],
        ]);

        return $result->choices[0]->message->content;
    }
}

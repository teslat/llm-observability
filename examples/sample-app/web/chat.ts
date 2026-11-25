import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

export async function draftReply(ticket: string) {
  const { text } = await generateText({
    model: openai('gpt-4o-mini'),
    prompt: `Draft a reply to: ${ticket}`,
  });
  return text;
}

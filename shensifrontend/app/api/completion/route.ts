import OpenAI from 'openai';
import { OpenAIStream, StreamingTextResponse } from 'ai';

export const runtime = 'edge';



export async function POST(req: Request) {
  // Extract the `prompt` from the body of the request
  const { prompt } = await req.json();
  const authHeader = req.headers.get('Authorization');
  const openai = new OpenAI({
    apiKey: authHeader,

    baseURL: `${process.env.PROXY_URL}/v1`
  });
  // Request the OpenAI API for the response based on the prompt
  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    stream: true,
    // a precise prompt is important for the AI to reply with the correct tokens
    messages: [
      {
        role: 'user',
        content: `${prompt}`,
      },
    ],

    temperature: 0, // you want absolute certainty for spell check
    top_p: 1,
    frequency_penalty: 1,
    presence_penalty: 1,
  });

  const stream = OpenAIStream(response);

  return new StreamingTextResponse(stream);
}
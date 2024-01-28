import OpenAI from 'openai'
import { OpenAIStream, StreamingTextResponse } from 'ai'


export const runtime = 'edge'

export async function POST(req: Request) {
  // Extract the `prompt` from the body of the request

  const authHeader = req.headers.get('Authorization');
  const openai = new OpenAI({
    apiKey: authHeader,

    baseURL: `${process.env.PROXY_URL}/v1`
  });

  const { messages } = await req.json()
  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    stream: true,
    messages,
    temperature: 0.7,

    top_p: 1,
    frequency_penalty: 0,
    presence_penalty: 0,
  })

  const stream = OpenAIStream(response)

  return new StreamingTextResponse(stream)
}
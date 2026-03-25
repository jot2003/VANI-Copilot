const API_KEY = 'vani-copilot-dev-key'

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
}

export async function sendMessage(message: string, conversationId?: string) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers,
    body: JSON.stringify({ message, conversation_id: conversationId }),
  })
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`)
  return res.json()
}

export async function streamMessage(
  message: string,
  conversationId: string | undefined,
  onToken: (token: string) => void,
  onDone: (data: {
    conversation_id: string
    sources: any[]
    intent?: string
    confidence?: number
    used_tools?: string[]
    handoff_suggested?: boolean
  }) => void,
) {
  const res = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { ...headers, Accept: 'text/event-stream' },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  })

  if (!res.ok) throw new Error(`Stream failed: ${res.status}`)

  const reader = res.body?.getReader()
  if (!reader) throw new Error('No reader')

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const jsonStr = line.slice(6).trim()
      if (!jsonStr) continue

      try {
        const chunk = JSON.parse(jsonStr)
        if (chunk.done) {
          onDone({
            conversation_id: chunk.conversation_id,
            sources: chunk.sources || [],
            intent: chunk.intent,
            confidence: chunk.confidence,
            used_tools: chunk.used_tools,
            handoff_suggested: chunk.handoff_suggested,
          })
        } else if (chunk.token) {
          onToken(chunk.token)
        }
      } catch {
        // skip malformed chunks
      }
    }
  }
}

export async function fetchConversations() {
  const res = await fetch('/api/conversations', { headers })
  if (!res.ok) throw new Error(`Fetch conversations failed: ${res.status}`)
  return res.json()
}

export async function fetchConversation(id: string) {
  const res = await fetch(`/api/conversations/${id}`, { headers })
  if (!res.ok) throw new Error(`Fetch conversation failed: ${res.status}`)
  return res.json()
}

export async function sendFeedback(conversationId: string, messageId: number, rating: number) {
  const res = await fetch('/api/feedback', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      conversation_id: conversationId,
      message_id: messageId,
      rating,
    }),
  })
  if (!res.ok) throw new Error(`Feedback failed: ${res.status}`)
  return res.json()
}

// --- Admin APIs ---

export async function fetchDocuments() {
  const res = await fetch('/api/admin/documents', { headers })
  if (!res.ok) throw new Error(`Fetch documents failed: ${res.status}`)
  return res.json()
}

export async function createDocument(filename: string, content: string, category: string = 'general') {
  const res = await fetch('/api/admin/documents', {
    method: 'POST',
    headers,
    body: JSON.stringify({ filename, content, category }),
  })
  if (!res.ok) throw new Error(`Create document failed: ${res.status}`)
  return res.json()
}

export async function deleteDocument(id: number) {
  const res = await fetch(`/api/admin/documents/${id}`, {
    method: 'DELETE',
    headers,
  })
  if (!res.ok) throw new Error(`Delete document failed: ${res.status}`)
  return res.json()
}

export async function fetchAnalyticsOverview() {
  const res = await fetch('/api/analytics/overview', { headers })
  if (!res.ok) throw new Error(`Fetch analytics failed: ${res.status}`)
  return res.json()
}

export async function fetchIntentStats(days: number = 30) {
  const res = await fetch(`/api/analytics/intents?days=${days}`, { headers })
  if (!res.ok) throw new Error(`Fetch intents failed: ${res.status}`)
  return res.json()
}

export async function fetchFeedbackList(limit: number = 20) {
  const res = await fetch(`/api/analytics/feedback?limit=${limit}`, { headers })
  if (!res.ok) throw new Error(`Fetch feedback failed: ${res.status}`)
  return res.json()
}

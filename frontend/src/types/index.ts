export interface SourceReference {
  content: string
  source_file: string
  score: number
}

export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant'
  content: string
  created_at?: string
  sources?: SourceReference[]
  isStreaming?: boolean
  intent?: string
  confidence?: number
  used_tools?: string[]
  handoff_suggested?: boolean
}

export interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface ConversationDetail extends Conversation {
  messages: ChatMessage[]
}

export interface StreamChunk {
  token: string
  done: boolean
  conversation_id: string
  sources: SourceReference[]
  intent?: string
  confidence?: number
  used_tools?: string[]
  handoff_suggested?: boolean
}

export interface KBDocument {
  id: number
  filename: string
  category: string
  chunk_count: number
  content_preview: string
  uploaded_at: string | null
  updated_at: string | null
}

export interface AnalyticsOverview {
  total_conversations: number
  total_messages: number
  conversations_last_7d: number
  avg_messages_per_conversation: number
  feedback: {
    total: number
    positive: number
    negative: number
    satisfaction_rate: number
  }
  intent_distribution: Record<string, number>
}

export type AppPage = 'chat' | 'admin'

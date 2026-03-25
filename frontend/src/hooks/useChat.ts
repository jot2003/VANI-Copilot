import { useCallback } from 'react'
import { streamMessage, fetchConversations } from '../services/api'
import { useChatStore } from '../store/chatStore'

export function useChat() {
  const {
    currentConversationId,
    isLoading,
    addMessage,
    appendToLastMessage,
    updateLastMessageSources,
    updateLastMessageMeta,
    setLoading,
    setCurrentConversation,
    setConversations,
  } = useChatStore()

  const send = useCallback(
    async (message: string) => {
      if (!message.trim() || isLoading) return

      addMessage({ role: 'user', content: message })
      addMessage({ role: 'assistant', content: '', isStreaming: true })
      setLoading(true)

      try {
        await streamMessage(
          message,
          currentConversationId ?? undefined,
          (token) => appendToLastMessage(token),
          (data) => {
            updateLastMessageSources(data.sources)
            updateLastMessageMeta({
              intent: data.intent,
              confidence: data.confidence,
              used_tools: data.used_tools,
              handoff_suggested: data.handoff_suggested,
            })
            if (!currentConversationId) {
              setCurrentConversation(data.conversation_id)
            }
            fetchConversations()
              .then((convs) => setConversations(convs))
              .catch(() => {})
          },
        )
      } catch (err) {
        appendToLastMessage('\n\n[Error: Could not get response. Check if backend is running.]')
      } finally {
        setLoading(false)
      }
    },
    [
      currentConversationId,
      isLoading,
      addMessage,
      appendToLastMessage,
      updateLastMessageSources,
      updateLastMessageMeta,
      setLoading,
      setCurrentConversation,
      setConversations,
    ],
  )

  return { send, isLoading }
}

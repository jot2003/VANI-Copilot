import { create } from 'zustand'
import type { AppPage, ChatMessage, Conversation, SourceReference } from '../types'

interface ChatState {
  currentPage: AppPage
  conversations: Conversation[]
  currentConversationId: string | null
  messages: ChatMessage[]
  isLoading: boolean
  isDarkMode: boolean
  sidebarOpen: boolean

  setPage: (page: AppPage) => void
  setConversations: (conversations: Conversation[]) => void
  setCurrentConversation: (id: string | null) => void
  setMessages: (messages: ChatMessage[]) => void
  addMessage: (message: ChatMessage) => void
  appendToLastMessage: (token: string) => void
  updateLastMessageSources: (sources: SourceReference[]) => void
  updateLastMessageMeta: (meta: Partial<ChatMessage>) => void
  finishStreaming: () => void
  setLoading: (loading: boolean) => void
  toggleDarkMode: () => void
  toggleSidebar: () => void
  newConversation: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  currentPage: 'chat' as AppPage,
  conversations: [],
  currentConversationId: null,
  messages: [],
  isLoading: false,
  isDarkMode: false,
  sidebarOpen: true,

  setPage: (page) => set({ currentPage: page }),
  setConversations: (conversations) => set({ conversations }),
  setCurrentConversation: (id) => set({ currentConversationId: id }),
  setMessages: (messages) => set({ messages }),

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  appendToLastMessage: (token) =>
    set((state) => {
      const msgs = [...state.messages]
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant') {
        msgs[msgs.length - 1] = { ...last, content: last.content + token }
      }
      return { messages: msgs }
    }),

  updateLastMessageSources: (sources) =>
    set((state) => {
      const msgs = [...state.messages]
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant') {
        msgs[msgs.length - 1] = { ...last, sources, isStreaming: false }
      }
      return { messages: msgs }
    }),

  updateLastMessageMeta: (meta) =>
    set((state) => {
      const msgs = [...state.messages]
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant') {
        msgs[msgs.length - 1] = { ...last, ...meta }
      }
      return { messages: msgs }
    }),

  finishStreaming: () =>
    set((state) => {
      const msgs = [...state.messages]
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant') {
        msgs[msgs.length - 1] = { ...last, isStreaming: false }
      }
      return { messages: msgs, isLoading: false }
    }),

  setLoading: (loading) => set({ isLoading: loading }),

  toggleDarkMode: () =>
    set((state) => {
      const newMode = !state.isDarkMode
      document.documentElement.classList.toggle('dark', newMode)
      return { isDarkMode: newMode }
    }),

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  newConversation: () =>
    set({ currentConversationId: null, messages: [] }),
}))

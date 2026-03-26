import { useEffect } from 'react'
import { Plus, MessageSquare, X, Zap, Clock } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useChatStore } from '../../store/chatStore'
import { fetchConversations, fetchConversation } from '../../services/api'

export function Sidebar() {
  const {
    conversations,
    currentConversationId,
    sidebarOpen,
    setConversations,
    setCurrentConversation,
    setMessages,
    newConversation,
    toggleSidebar,
    setPage,
  } = useChatStore()

  useEffect(() => {
    fetchConversations()
      .then(setConversations)
      .catch(() => {})
  }, [setConversations])

  const handleSelectConversation = async (id: string) => {
    try {
      const detail = await fetchConversation(id)
      setCurrentConversation(id)
      setMessages(detail.messages)
      setPage('chat')
    } catch {
      // ignore
    }
  }

  return (
    <AnimatePresence>
      {sidebarOpen && (
        <motion.aside
          initial={{ x: -280 }}
          animate={{ x: 0 }}
          exit={{ x: -280 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="flex h-full w-[280px] shrink-0 flex-col border-r border-border dark:border-dark-border bg-card dark:bg-dark-card"
        >
          {/* Brand */}
          <div className="flex items-center gap-2.5 p-4 pb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-500 shadow-md shadow-primary/20">
              <Zap size={16} className="text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-sm font-bold tracking-tight">VANI Copilot</h1>
              <p className="text-[10px] text-muted">v2.0 — Agent + RAG</p>
            </div>
            <button
              onClick={toggleSidebar}
              className="rounded-lg p-1 hover:bg-secondary dark:hover:bg-dark-secondary transition-colors lg:hidden"
            >
              <X size={16} />
            </button>
          </div>

          {/* New Chat */}
          <div className="px-3 mb-4">
            <button
              onClick={() => { newConversation(); setPage('chat') }}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-primary to-purple-500 px-3 py-2.5 text-sm font-medium text-white shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/30 transition-all active:scale-[0.98]"
            >
              <Plus size={16} />
              New Conversation
            </button>
          </div>

          {/* Section label */}
          <div className="px-4 mb-2 flex items-center gap-1.5">
            <Clock size={10} className="text-muted" />
            <p className="text-[10px] font-medium uppercase tracking-wider text-muted">
              Recent
            </p>
          </div>

          {/* Conversations */}
          <div className="flex-1 overflow-y-auto px-3 pb-3">
            {conversations.length === 0 ? (
              <div className="px-3 py-8 text-center">
                <MessageSquare size={24} className="mx-auto mb-2 text-muted/40" />
                <p className="text-xs text-muted">No conversations yet</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`group mb-0.5 flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm transition-all ${
                    currentConversationId === conv.id
                      ? 'bg-primary/10 text-primary font-medium'
                      : 'text-foreground/70 dark:text-dark-foreground/70 hover:bg-secondary dark:hover:bg-dark-secondary'
                  }`}
                >
                  <MessageSquare size={14} className={`shrink-0 ${
                    currentConversationId === conv.id ? 'text-primary' : 'opacity-40 group-hover:opacity-70'
                  } transition-opacity`} />
                  <span className="truncate">{conv.title}</span>
                </button>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-border dark:border-dark-border p-3">
            <div className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-primary/5 to-purple-500/5 dark:from-primary/10 dark:to-purple-500/10 px-3 py-2">
              <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
              <span className="text-[11px] text-muted">System online</span>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}

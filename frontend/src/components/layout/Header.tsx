import { Menu, Moon, Sun, Settings, MessageSquare } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'

export function Header() {
  const { isDarkMode, currentPage, toggleDarkMode, toggleSidebar, setPage } = useChatStore()

  return (
    <header className="flex h-14 items-center justify-between border-b border-border dark:border-dark-border bg-card dark:bg-dark-card px-4">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="rounded p-1.5 hover:bg-secondary dark:hover:bg-dark-secondary transition-colors"
        >
          <Menu size={20} />
        </button>
        <div>
          <h1 className="text-sm font-semibold">VANI Copilot</h1>
          <p className="text-xs text-muted">AI Customer Support Assistant</p>
        </div>
      </div>

      <div className="flex items-center gap-1">
        <button
          onClick={() => setPage('chat')}
          className={`rounded-lg p-2 transition-colors ${
            currentPage === 'chat'
              ? 'bg-primary/10 text-primary'
              : 'text-muted hover:bg-secondary dark:hover:bg-dark-secondary'
          }`}
          title="Chat"
        >
          <MessageSquare size={18} />
        </button>
        <button
          onClick={() => setPage('admin')}
          className={`rounded-lg p-2 transition-colors ${
            currentPage === 'admin'
              ? 'bg-primary/10 text-primary'
              : 'text-muted hover:bg-secondary dark:hover:bg-dark-secondary'
          }`}
          title="Admin Dashboard"
        >
          <Settings size={18} />
        </button>
        <div className="mx-1 h-5 w-px bg-border dark:bg-dark-border" />
        <button
          onClick={toggleDarkMode}
          className="rounded-lg p-2 hover:bg-secondary dark:hover:bg-dark-secondary transition-colors"
          title="Toggle dark mode"
        >
          {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  )
}

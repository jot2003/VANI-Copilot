import { Menu, Moon, Sun, Settings, MessageSquare, Zap } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'

export function Header() {
  const { isDarkMode, currentPage, toggleDarkMode, toggleSidebar, setPage } = useChatStore()

  return (
    <header className="glass flex h-14 items-center justify-between border-b border-border dark:border-dark-border px-4 z-10">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="rounded-lg p-1.5 hover:bg-secondary dark:hover:bg-dark-secondary transition-colors"
        >
          <Menu size={20} />
        </button>
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-purple-500">
            <Zap size={14} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight">VANI Copilot</h1>
            <p className="text-[10px] text-muted leading-none">AI Customer Support</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-0.5">
        <NavButton
          active={currentPage === 'chat'}
          onClick={() => setPage('chat')}
          title="Chat"
        >
          <MessageSquare size={16} />
        </NavButton>
        <NavButton
          active={currentPage === 'admin'}
          onClick={() => setPage('admin')}
          title="Dashboard"
        >
          <Settings size={16} />
        </NavButton>
        <div className="mx-1.5 h-5 w-px bg-border dark:bg-dark-border" />
        <button
          onClick={toggleDarkMode}
          className="rounded-lg p-2 hover:bg-secondary dark:hover:bg-dark-secondary transition-all active:scale-95"
          title="Toggle theme"
        >
          {isDarkMode ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </header>
  )
}

function NavButton({
  active,
  onClick,
  title,
  children,
}: {
  active: boolean
  onClick: () => void
  title: string
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      className={`relative rounded-lg p-2 transition-all active:scale-95 ${
        active
          ? 'text-primary'
          : 'text-muted hover:text-foreground dark:hover:text-dark-foreground hover:bg-secondary dark:hover:bg-dark-secondary'
      }`}
      title={title}
    >
      {children}
      {active && (
        <span className="absolute bottom-0.5 left-1/2 -translate-x-1/2 h-0.5 w-4 rounded-full bg-primary" />
      )}
    </button>
  )
}

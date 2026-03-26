import type { ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

interface Props {
  children: ReactNode
}

export function Layout({ children }: Props) {
  return (
    <div className="flex h-screen bg-background dark:bg-dark-background text-foreground dark:text-dark-foreground">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-hidden bg-gradient-to-b from-background via-background to-accent/5 dark:from-dark-background dark:via-dark-background dark:to-dark-accent/10">
          {children}
        </main>
      </div>
    </div>
  )
}

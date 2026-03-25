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
        <main className="flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  )
}

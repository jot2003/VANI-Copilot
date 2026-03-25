import { useChatStore } from './store/chatStore'
import { Layout } from './components/layout/Layout'
import { ChatWindow } from './components/chat/ChatWindow'
import { AdminDashboard } from './components/admin/AdminDashboard'

function App() {
  const { currentPage } = useChatStore()

  return (
    <Layout>
      {currentPage === 'chat' && <ChatWindow />}
      {currentPage === 'admin' && <AdminDashboard />}
    </Layout>
  )
}

export default App

import { useEffect, useState } from 'react'
import {
  FileText,
  Upload,
  Trash2,
  BarChart3,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
} from 'lucide-react'
import type { KBDocument, AnalyticsOverview } from '../../types'
import {
  fetchDocuments,
  createDocument,
  deleteDocument,
  fetchAnalyticsOverview,
} from '../../services/api'

type Tab = 'knowledge' | 'analytics'

export function AdminDashboard() {
  const [tab, setTab] = useState<Tab>('knowledge')

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border dark:border-dark-border bg-card dark:bg-dark-card px-6 pt-4">
        <h2 className="text-lg font-semibold mb-3">Admin Dashboard</h2>
        <div className="flex gap-1">
          <TabButton active={tab === 'knowledge'} onClick={() => setTab('knowledge')}>
            <FileText size={14} /> Knowledge Base
          </TabButton>
          <TabButton active={tab === 'analytics'} onClick={() => setTab('analytics')}>
            <BarChart3 size={14} /> Analytics
          </TabButton>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {tab === 'knowledge' && <KnowledgeBaseTab />}
        {tab === 'analytics' && <AnalyticsTab />}
      </div>
    </div>
  )
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
        active
          ? 'bg-background dark:bg-dark-background text-foreground dark:text-dark-foreground border border-b-0 border-border dark:border-dark-border'
          : 'text-muted hover:text-foreground dark:hover:text-dark-foreground'
      }`}
    >
      {children}
    </button>
  )
}

// --- Knowledge Base Tab ---

function KnowledgeBaseTab() {
  const [docs, setDocs] = useState<KBDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [showUpload, setShowUpload] = useState(false)
  const [newFilename, setNewFilename] = useState('')
  const [newContent, setNewContent] = useState('')
  const [newCategory, setNewCategory] = useState('general')

  const loadDocs = () => {
    setLoading(true)
    fetchDocuments()
      .then((data) => setDocs(data.documents || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadDocs() }, [])

  const handleCreate = async () => {
    if (!newFilename || !newContent) return
    const fname = newFilename.endsWith('.txt') ? newFilename : newFilename + '.txt'
    await createDocument(fname, newContent, newCategory)
    setNewFilename('')
    setNewContent('')
    setShowUpload(false)
    loadDocs()
  }

  const handleDelete = async (id: number, filename: string) => {
    if (!confirm(`Delete "${filename}"? FAISS index will be rebuilt.`)) return
    await deleteDocument(id)
    loadDocs()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted">{docs.length} documents in knowledge base</p>
        <div className="flex gap-2">
          <button
            onClick={loadDocs}
            className="flex items-center gap-1.5 rounded-lg border border-border dark:border-dark-border px-3 py-1.5 text-sm hover:bg-secondary dark:hover:bg-dark-secondary transition-colors"
          >
            <RefreshCw size={14} /> Refresh
          </button>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="flex items-center gap-1.5 rounded-lg bg-primary text-primary-foreground px-3 py-1.5 text-sm hover:opacity-90 transition-opacity"
          >
            <Upload size={14} /> Add Document
          </button>
        </div>
      </div>

      {showUpload && (
        <div className="mb-4 rounded-lg border border-border dark:border-dark-border p-4 bg-secondary/50 dark:bg-dark-card">
          <div className="grid grid-cols-2 gap-3 mb-3">
            <input
              type="text"
              placeholder="Filename (e.g. shipping-policy.txt)"
              value={newFilename}
              onChange={(e) => setNewFilename(e.target.value)}
              className="rounded-lg border border-border dark:border-dark-border bg-background dark:bg-dark-background px-3 py-2 text-sm"
            />
            <select
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              className="rounded-lg border border-border dark:border-dark-border bg-background dark:bg-dark-background px-3 py-2 text-sm"
            >
              <option value="general">General</option>
              <option value="faq">FAQ</option>
              <option value="policies">Policies</option>
              <option value="products">Products</option>
            </select>
          </div>
          <textarea
            placeholder="Paste document content here..."
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            className="w-full rounded-lg border border-border dark:border-dark-border bg-background dark:bg-dark-background px-3 py-2 text-sm h-32 resize-none"
          />
          <div className="mt-3 flex justify-end gap-2">
            <button
              onClick={() => setShowUpload(false)}
              className="px-3 py-1.5 text-sm text-muted hover:text-foreground transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={!newFilename || !newContent}
              className="rounded-lg bg-primary text-primary-foreground px-4 py-1.5 text-sm disabled:opacity-50"
            >
              Save & Rebuild Index
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <p className="text-sm text-muted">Loading...</p>
      ) : (
        <div className="space-y-2">
          {docs.map((doc) => (
            <div
              key={doc.id}
              className="flex items-start justify-between rounded-lg border border-border dark:border-dark-border p-4 bg-card dark:bg-dark-card"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-primary shrink-0" />
                  <span className="font-medium text-sm">{doc.filename}</span>
                  <span className="rounded-full bg-accent dark:bg-dark-background px-2 py-0.5 text-xs text-muted">
                    {doc.category}
                  </span>
                  <span className="text-xs text-muted">
                    {doc.chunk_count} chunks
                  </span>
                </div>
                <p className="mt-1 text-xs text-muted line-clamp-2">{doc.content_preview}</p>
              </div>
              <button
                onClick={() => handleDelete(doc.id, doc.filename)}
                className="ml-3 rounded p-1.5 text-muted hover:text-destructive hover:bg-destructive/10 transition-colors"
                title="Delete document"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// --- Analytics Tab ---

function AnalyticsTab() {
  const [data, setData] = useState<AnalyticsOverview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalyticsOverview()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-sm text-muted">Loading analytics...</p>
  if (!data) return <p className="text-sm text-muted">Failed to load analytics.</p>

  const intentEntries = Object.entries(data.intent_distribution).sort((a, b) => b[1] - a[1])
  const maxIntent = intentEntries.length > 0 ? intentEntries[0][1] : 1

  const intentLabels: Record<string, string> = {
    faq: 'FAQ / Chính sách',
    order_tracking: 'Tra đơn hàng',
    product_inquiry: 'Hỏi sản phẩm',
    chitchat: 'Chào hỏi',
    handoff: 'Chuyển nhân viên',
    general: 'Chung',
  }

  return (
    <div>
      {/* Stats cards */}
      <div className="grid grid-cols-2 gap-4 mb-6 lg:grid-cols-4">
        <StatCard
          icon={<MessageSquare size={20} />}
          label="Total Conversations"
          value={data.total_conversations}
        />
        <StatCard
          icon={<MessageSquare size={20} />}
          label="Last 7 days"
          value={data.conversations_last_7d}
        />
        <StatCard
          icon={<ThumbsUp size={20} />}
          label="Satisfaction Rate"
          value={`${data.feedback.satisfaction_rate}%`}
        />
        <StatCard
          icon={<ThumbsDown size={20} />}
          label="Negative Feedback"
          value={data.feedback.negative}
        />
      </div>

      {/* Intent distribution */}
      <div className="rounded-lg border border-border dark:border-dark-border p-4 bg-card dark:bg-dark-card">
        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <BarChart3 size={16} /> Intent Distribution
        </h3>
        {intentEntries.length === 0 ? (
          <p className="text-sm text-muted">No data yet. Start chatting to see intent analytics.</p>
        ) : (
          <div className="space-y-2">
            {intentEntries.map(([intent, count]) => (
              <div key={intent} className="flex items-center gap-3">
                <span className="w-32 text-xs text-right text-muted truncate">
                  {intentLabels[intent] || intent}
                </span>
                <div className="flex-1 h-5 bg-secondary dark:bg-dark-background rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${(count / maxIntent) * 100}%` }}
                  />
                </div>
                <span className="w-8 text-xs font-medium text-right">{count}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string | number
}) {
  return (
    <div className="rounded-lg border border-border dark:border-dark-border p-4 bg-card dark:bg-dark-card">
      <div className="flex items-center gap-2 text-muted mb-2">{icon}<span className="text-xs">{label}</span></div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  )
}

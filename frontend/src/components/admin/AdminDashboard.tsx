import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText,
  Trash2,
  BarChart3,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  TrendingUp,
  Loader2,
  Plus,
  X,
} from 'lucide-react'
import { toast } from 'sonner'
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
      <div className="border-b border-border dark:border-dark-border glass px-6 pt-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-500 shadow-sm">
            <BarChart3 size={16} className="text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold tracking-tight">Admin Dashboard</h2>
            <p className="text-xs text-muted">Manage knowledge base & analytics</p>
          </div>
        </div>
        <div className="flex gap-1">
          <TabButton active={tab === 'knowledge'} onClick={() => setTab('knowledge')}>
            <FileText size={14} /> Knowledge Base
          </TabButton>
          <TabButton active={tab === 'analytics'} onClick={() => setTab('analytics')}>
            <TrendingUp size={14} /> Analytics
          </TabButton>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={tab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
          >
            {tab === 'knowledge' && <KnowledgeBaseTab />}
            {tab === 'analytics' && <AnalyticsTab />}
          </motion.div>
        </AnimatePresence>
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
      className={`relative flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium transition-colors ${
        active
          ? 'text-primary'
          : 'text-muted hover:text-foreground dark:hover:text-dark-foreground'
      }`}
    >
      {children}
      {active && (
        <motion.span
          layoutId="admin-tab"
          className="absolute bottom-0 left-2 right-2 h-0.5 rounded-full bg-primary"
        />
      )}
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
  const [creating, setCreating] = useState(false)

  const loadDocs = () => {
    setLoading(true)
    fetchDocuments()
      .then((data) => setDocs(data.documents || []))
      .catch(() => toast.error('Failed to load documents'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadDocs() }, [])

  const handleCreate = async () => {
    if (!newFilename || !newContent) return
    setCreating(true)
    try {
      const fname = newFilename.endsWith('.txt') ? newFilename : newFilename + '.txt'
      await createDocument(fname, newContent, newCategory)
      toast.success('Document created & index rebuilt')
      setNewFilename('')
      setNewContent('')
      setShowUpload(false)
      loadDocs()
    } catch {
      toast.error('Failed to create document')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id: number, filename: string) => {
    if (!confirm(`Delete "${filename}"? FAISS index will be rebuilt.`)) return
    try {
      await deleteDocument(id)
      toast.success(`"${filename}" deleted`)
      loadDocs()
    } catch {
      toast.error('Failed to delete document')
    }
  }

  return (
    <div className="max-w-4xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-sm font-medium">{docs.length} documents</p>
          <p className="text-xs text-muted">in knowledge base</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadDocs}
            className="flex items-center gap-1.5 rounded-xl border border-border dark:border-dark-border px-3 py-2 text-xs font-medium hover:bg-secondary dark:hover:bg-dark-secondary transition-colors"
          >
            <RefreshCw size={13} /> Refresh
          </button>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-primary to-purple-500 text-white px-4 py-2 text-xs font-medium shadow-sm shadow-primary/20 hover:shadow-md hover:shadow-primary/25 transition-all active:scale-[0.98]"
          >
            {showUpload ? <X size={13} /> : <Plus size={13} />}
            {showUpload ? 'Cancel' : 'Add Document'}
          </button>
        </div>
      </div>

      {/* Upload form */}
      <AnimatePresence>
        {showUpload && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-5 overflow-hidden"
          >
            <div className="rounded-2xl border border-border dark:border-dark-border p-5 bg-card dark:bg-dark-card">
              <div className="grid grid-cols-2 gap-3 mb-3">
                <input
                  type="text"
                  placeholder="Filename (e.g. shipping-policy.txt)"
                  value={newFilename}
                  onChange={(e) => setNewFilename(e.target.value)}
                  className="rounded-xl border border-border dark:border-dark-border bg-background dark:bg-dark-background px-3 py-2.5 text-sm outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                />
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="rounded-xl border border-border dark:border-dark-border bg-background dark:bg-dark-background px-3 py-2.5 text-sm outline-none focus:border-primary/50 transition-all"
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
                className="w-full rounded-xl border border-border dark:border-dark-border bg-background dark:bg-dark-background px-3 py-2.5 text-sm h-32 resize-none outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
              />
              <div className="mt-3 flex justify-end">
                <button
                  onClick={handleCreate}
                  disabled={!newFilename || !newContent || creating}
                  className="flex items-center gap-2 rounded-xl bg-primary text-white px-5 py-2.5 text-sm font-medium disabled:opacity-50 hover:opacity-90 transition-all active:scale-[0.98]"
                >
                  {creating && <Loader2 size={14} className="animate-spin" />}
                  Save & Rebuild Index
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Documents list */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={20} className="animate-spin text-primary" />
        </div>
      ) : (
        <div className="space-y-2">
          {docs.map((doc) => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-start justify-between rounded-2xl border border-border dark:border-dark-border p-4 bg-card dark:bg-dark-card hover:border-primary/20 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <FileText size={14} className="text-primary shrink-0" />
                  <span className="font-medium text-sm">{doc.filename}</span>
                  <span className="rounded-full bg-accent/60 dark:bg-dark-accent/60 border border-border/50 dark:border-dark-border/50 px-2 py-0.5 text-[10px] text-muted font-medium">
                    {doc.category}
                  </span>
                  <span className="text-[10px] text-muted">
                    {doc.chunk_count} chunks
                  </span>
                </div>
                <p className="mt-1.5 text-xs text-muted line-clamp-2 leading-relaxed">{doc.content_preview}</p>
              </div>
              <button
                onClick={() => handleDelete(doc.id, doc.filename)}
                className="ml-3 rounded-xl p-2 text-muted hover:text-destructive hover:bg-destructive/10 transition-all active:scale-90"
                title="Delete"
              >
                <Trash2 size={14} />
              </button>
            </motion.div>
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
      .catch(() => toast.error('Failed to load analytics'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 size={20} className="animate-spin text-primary" />
      </div>
    )
  }
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
    rag: 'RAG Direct',
  }

  const intentColors: Record<string, string> = {
    faq: 'from-blue-500 to-blue-600',
    order_tracking: 'from-amber-500 to-amber-600',
    product_inquiry: 'from-purple-500 to-purple-600',
    chitchat: 'from-emerald-500 to-emerald-600',
    handoff: 'from-rose-500 to-rose-600',
    general: 'from-slate-500 to-slate-600',
    rag: 'from-cyan-500 to-cyan-600',
  }

  return (
    <div className="max-w-4xl">
      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-4 mb-6 lg:grid-cols-4">
        <StatCard
          icon={<MessageSquare size={18} />}
          label="Total Conversations"
          value={data.total_conversations}
          gradient="from-primary/10 to-purple-500/10"
          iconColor="text-primary"
        />
        <StatCard
          icon={<TrendingUp size={18} />}
          label="Last 7 Days"
          value={data.conversations_last_7d}
          gradient="from-cyan-500/10 to-blue-500/10"
          iconColor="text-cyan-500"
        />
        <StatCard
          icon={<ThumbsUp size={18} />}
          label="Satisfaction"
          value={`${data.feedback.satisfaction_rate}%`}
          gradient="from-emerald-500/10 to-green-500/10"
          iconColor="text-emerald-500"
        />
        <StatCard
          icon={<ThumbsDown size={18} />}
          label="Negative"
          value={data.feedback.negative}
          gradient="from-rose-500/10 to-red-500/10"
          iconColor="text-rose-500"
        />
      </div>

      {/* Additional stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="rounded-2xl border border-border dark:border-dark-border p-4 bg-card dark:bg-dark-card">
          <p className="text-xs text-muted mb-1">Total Messages</p>
          <p className="text-2xl font-bold">{data.total_messages}</p>
        </div>
        <div className="rounded-2xl border border-border dark:border-dark-border p-4 bg-card dark:bg-dark-card">
          <p className="text-xs text-muted mb-1">Avg Messages / Conv</p>
          <p className="text-2xl font-bold">{data.avg_messages_per_conversation}</p>
        </div>
      </div>

      {/* Intent distribution */}
      <div className="rounded-2xl border border-border dark:border-dark-border p-5 bg-card dark:bg-dark-card">
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <BarChart3 size={16} className="text-primary" /> Intent Distribution
        </h3>
        {intentEntries.length === 0 ? (
          <p className="text-sm text-muted py-4">No data yet. Start chatting to see intent analytics.</p>
        ) : (
          <div className="space-y-3">
            {intentEntries.map(([intent, count]) => (
              <div key={intent} className="flex items-center gap-3">
                <span className="w-28 text-xs text-right text-muted truncate">
                  {intentLabels[intent] || intent}
                </span>
                <div className="flex-1 h-6 bg-secondary dark:bg-dark-secondary rounded-lg overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(count / maxIntent) * 100}%` }}
                    transition={{ duration: 0.6, ease: 'easeOut' }}
                    className={`h-full bg-gradient-to-r ${intentColors[intent] || 'from-slate-500 to-slate-600'} rounded-lg flex items-center justify-end pr-2`}
                  >
                    {count / maxIntent > 0.15 && (
                      <span className="text-[10px] font-bold text-white">{count}</span>
                    )}
                  </motion.div>
                </div>
                {count / maxIntent <= 0.15 && (
                  <span className="w-8 text-xs font-medium text-right">{count}</span>
                )}
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
  gradient,
  iconColor,
}: {
  icon: React.ReactNode
  label: string
  value: string | number
  gradient: string
  iconColor: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl border border-border dark:border-dark-border p-4 bg-gradient-to-br ${gradient} dark:bg-card`}
    >
      <div className={`flex items-center gap-2 mb-3 ${iconColor}`}>
        {icon}
        <span className="text-[11px] text-muted font-medium">{label}</span>
      </div>
      <p className="text-2xl font-bold tracking-tight">{value}</p>
    </motion.div>
  )
}

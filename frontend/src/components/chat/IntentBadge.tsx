import { Search, Package, ShoppingBag, MessageCircle, UserCheck, Cpu } from 'lucide-react'

const intentConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  faq: {
    label: 'FAQ',
    color: 'bg-blue-500/10 text-blue-500 dark:bg-blue-400/10 dark:text-blue-400 border-blue-500/20',
    icon: <Search size={10} />,
  },
  order_tracking: {
    label: 'Đơn hàng',
    color: 'bg-amber-500/10 text-amber-600 dark:bg-amber-400/10 dark:text-amber-400 border-amber-500/20',
    icon: <Package size={10} />,
  },
  product_inquiry: {
    label: 'Sản phẩm',
    color: 'bg-purple-500/10 text-purple-600 dark:bg-purple-400/10 dark:text-purple-400 border-purple-500/20',
    icon: <ShoppingBag size={10} />,
  },
  chitchat: {
    label: 'Chat',
    color: 'bg-emerald-500/10 text-emerald-600 dark:bg-emerald-400/10 dark:text-emerald-400 border-emerald-500/20',
    icon: <MessageCircle size={10} />,
  },
  handoff: {
    label: 'Chuyển NV',
    color: 'bg-rose-500/10 text-rose-600 dark:bg-rose-400/10 dark:text-rose-400 border-rose-500/20',
    icon: <UserCheck size={10} />,
  },
  general: {
    label: 'Chung',
    color: 'bg-slate-500/10 text-slate-500 dark:bg-slate-400/10 dark:text-slate-400 border-slate-500/20',
    icon: <MessageCircle size={10} />,
  },
  rag: {
    label: 'RAG',
    color: 'bg-cyan-500/10 text-cyan-600 dark:bg-cyan-400/10 dark:text-cyan-400 border-cyan-500/20',
    icon: <Cpu size={10} />,
  },
}

export function IntentBadge({ intent, tools }: { intent?: string; tools?: string[] }) {
  if (!intent) return null
  const config = intentConfig[intent] || intentConfig.general

  return (
    <div className="flex items-center gap-1.5 mt-1.5 px-1">
      <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium ${config.color}`}>
        {config.icon} {config.label}
      </span>
      {tools && tools.length > 0 && tools[0] !== 'fallback_rag' && (
        <span className="text-[10px] text-muted font-mono">
          {tools.join(' → ')}
        </span>
      )}
    </div>
  )
}

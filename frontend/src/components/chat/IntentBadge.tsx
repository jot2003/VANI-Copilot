import { Search, Package, ShoppingBag, MessageCircle, UserCheck } from 'lucide-react'

const intentConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  faq: { label: 'FAQ', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300', icon: <Search size={10} /> },
  order_tracking: { label: 'Đơn hàng', color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300', icon: <Package size={10} /> },
  product_inquiry: { label: 'Sản phẩm', color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300', icon: <ShoppingBag size={10} /> },
  chitchat: { label: 'Chat', color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300', icon: <MessageCircle size={10} /> },
  handoff: { label: 'Chuyển NV', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300', icon: <UserCheck size={10} /> },
  general: { label: 'Chung', color: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400', icon: <MessageCircle size={10} /> },
}

export function IntentBadge({ intent, tools }: { intent?: string; tools?: string[] }) {
  if (!intent) return null
  const config = intentConfig[intent] || intentConfig.general

  return (
    <div className="flex items-center gap-1.5 mt-1">
      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${config.color}`}>
        {config.icon} {config.label}
      </span>
      {tools && tools.length > 0 && tools[0] !== 'fallback_rag' && (
        <span className="text-[10px] text-muted">
          via {tools.join(', ')}
        </span>
      )}
    </div>
  )
}

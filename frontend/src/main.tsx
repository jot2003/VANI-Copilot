import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Toaster } from 'sonner'
import './index.css'
import App from './App'

document.documentElement.classList.add('dark')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
    <Toaster
      position="top-right"
      toastOptions={{
        className: 'glass !border-border dark:!border-dark-border !text-sm',
      }}
      theme="dark"
      richColors
    />
  </StrictMode>,
)

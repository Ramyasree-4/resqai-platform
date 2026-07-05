import * as Dialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { cn } from '@/utils/cn'

interface ModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: string
  description?: string
  children: React.ReactNode
  className?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
}

export function Modal({
  open,
  onOpenChange,
  title,
  description,
  children,
  className,
  size = 'md',
}: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm data-[state=open]:animate-fade-in" />
        <Dialog.Content
          className={cn(
            'fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2',
            'w-full p-0 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl',
            'border border-gray-200 dark:border-gray-700',
            'focus:outline-none data-[state=open]:animate-slide-in',
            sizeClasses[size],
            className
          )}
        >
          {/* Header */}
          {(title || description) && (
            <div className="px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex items-start justify-between gap-4">
              <div>
                {title && (
                  <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-white">
                    {title}
                  </Dialog.Title>
                )}
                {description && (
                  <Dialog.Description className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                    {description}
                  </Dialog.Description>
                )}
              </div>
              <Dialog.Close className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-shrink-0">
                <X className="w-4 h-4" />
              </Dialog.Close>
            </div>
          )}

          {/* Body */}
          <div className="px-6 py-4">{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

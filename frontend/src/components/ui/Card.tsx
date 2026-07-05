import { cn } from '@/utils/cn'

interface CardProps {
  children: React.ReactNode
  className?: string
  interactive?: boolean
  onClick?: () => void
}

export function Card({ children, className, interactive, onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800',
        'shadow-sm',
        interactive && 'hover:shadow-md transition-shadow duration-200 cursor-pointer',
        className
      )}
    >
      {children}
    </div>
  )
}

export function CardHeader({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        'px-5 py-4 border-b border-gray-100 dark:border-gray-800',
        className
      )}
    >
      {children}
    </div>
  )
}

export function CardContent({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return <div className={cn('px-5 py-4', className)}>{children}</div>
}

export function CardFooter({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        'px-5 py-3 border-t border-gray-100 dark:border-gray-800',
        className
      )}
    >
      {children}
    </div>
  )
}

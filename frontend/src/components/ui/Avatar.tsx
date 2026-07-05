import { cn } from '@/utils/cn'

interface AvatarProps {
  name?: string
  src?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizes = { sm: 'h-7 w-7 text-xs', md: 'h-9 w-9 text-sm', lg: 'h-12 w-12 text-base', xl: 'h-16 w-16 text-xl' }

function getInitials(name?: string) {
  if (!name) return '?'
  const parts = name.trim().split(' ')
  if (parts.length >= 2) return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
  return name.slice(0, 2).toUpperCase()
}

function getColor(name?: string) {
  const colors = ['bg-blue-500', 'bg-purple-500', 'bg-green-500', 'bg-orange-500', 'bg-pink-500', 'bg-indigo-500']
  if (!name) return colors[0]
  const idx = name.charCodeAt(0) % colors.length
  return colors[idx]
}

export function Avatar({ name, src, size = 'md', className }: AvatarProps) {
  return (
    <div className={cn('relative flex shrink-0 overflow-hidden rounded-full', sizes[size], className)}>
      {src ? (
        <img src={src} alt={name} className="h-full w-full object-cover" />
      ) : (
        <div className={cn('flex h-full w-full items-center justify-center text-white font-semibold', getColor(name))}>
          {getInitials(name)}
        </div>
      )}
    </div>
  )
}

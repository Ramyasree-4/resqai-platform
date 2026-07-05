import * as RadixSelect from '@radix-ui/react-select'
import { ChevronDown, Check } from 'lucide-react'
import { cn } from '@/utils/cn'

interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

interface SelectProps {
  value?: string
  onValueChange?: (value: string) => void
  options: SelectOption[]
  placeholder?: string
  label?: string
  error?: string
  disabled?: boolean
  className?: string
}

export function Select({
  value,
  onValueChange,
  options,
  placeholder = 'Select...',
  label,
  error,
  disabled,
  className,
}: SelectProps) {
  return (
    <div className={cn('w-full', className)}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {label}
        </label>
      )}
      <RadixSelect.Root value={value} onValueChange={onValueChange} disabled={disabled}>
        <RadixSelect.Trigger
          className={cn(
            'w-full flex items-center justify-between px-3 py-2.5 text-sm rounded-lg border',
            'bg-white dark:bg-gray-900 text-gray-900 dark:text-white',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            error
              ? 'border-red-500'
              : 'border-gray-300 dark:border-gray-700'
          )}
        >
          <RadixSelect.Value placeholder={placeholder} />
          <RadixSelect.Icon>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </RadixSelect.Icon>
        </RadixSelect.Trigger>

        <RadixSelect.Portal>
          <RadixSelect.Content
            className={cn(
              'z-50 bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700',
              'overflow-hidden animate-slide-in'
            )}
          >
            <RadixSelect.Viewport className="p-1">
              {options.map((option) => (
                <RadixSelect.Item
                  key={option.value}
                  value={option.value}
                  disabled={option.disabled}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 text-sm rounded-lg',
                    'text-gray-700 dark:text-gray-300',
                    'cursor-pointer select-none outline-none',
                    'focus:bg-blue-50 dark:focus:bg-blue-900/30 focus:text-blue-600 dark:focus:text-blue-400',
                    'data-[disabled]:opacity-50 data-[disabled]:cursor-not-allowed'
                  )}
                >
                  <RadixSelect.ItemIndicator>
                    <Check className="w-4 h-4 text-blue-600" />
                  </RadixSelect.ItemIndicator>
                  <RadixSelect.ItemText>{option.label}</RadixSelect.ItemText>
                </RadixSelect.Item>
              ))}
            </RadixSelect.Viewport>
          </RadixSelect.Content>
        </RadixSelect.Portal>
      </RadixSelect.Root>
      {error && (
        <p className="mt-1 text-xs text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  )
}

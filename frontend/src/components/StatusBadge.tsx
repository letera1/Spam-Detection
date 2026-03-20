interface StatusBadgeProps {
  isHealthy: boolean | null
}

export default function StatusBadge({ isHealthy }: StatusBadgeProps) {
  if (isHealthy === null) {
    return (
      <div className="flex items-center space-x-2 text-xs text-gray-500">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
        <span>Checking...</span>
      </div>
    )
  }

  return (
    <div className="flex items-center space-x-2">
      <div
        className={`w-2 h-2 rounded-full ${
          isHealthy ? 'bg-green-500' : 'bg-red-500'
        }`}
      />
      <span
        className={`text-xs font-medium ${
          isHealthy ? 'text-green-600' : 'text-red-600'
        }`}
      >
        {isHealthy ? 'Model Ready' : 'Model Offline'}
      </span>
    </div>
  )
}

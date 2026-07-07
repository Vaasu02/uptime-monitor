import StatusBadge from './StatusBadge'

function URLList({ urls, onDelete }) {
  if (urls.length === 0) {
    return (
      <p className="text-center text-gray-400 mt-8">
        No URLs being monitored. Add one above.
      </p>
    )
  }

  return (
    <div className="mt-6 space-y-3">
      {urls.map((url) => (
        <div
          key={url.id}
          className="flex items-center justify-between bg-gray-800 rounded-lg p-4 border border-gray-700"
        >
          <div className="flex items-center gap-3 min-w-0">
            <StatusBadge check={url.latest_check} />
            <div className="min-w-0">
              <p className="font-medium truncate">
                {url.name || url.url}
              </p>
              {url.name && (
                <p className="text-sm text-gray-400 truncate">{url.url}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-4 shrink-0 ml-4">
            {url.latest_check && (
              <div className="text-right text-sm">
                <p className="text-gray-300">
                  {url.latest_check.response_time_ms
                    ? `${Math.round(url.latest_check.response_time_ms)} ms`
                    : '—'}
                </p>
                <p className="text-gray-500">
                  {new Date(url.latest_check.checked_at).toLocaleTimeString()}
                </p>
              </div>
            )}
            {!url.latest_check && (
              <p className="text-sm text-gray-500">Pending...</p>
            )}
            <button
              onClick={() => onDelete(url.id)}
              className="text-gray-500 hover:text-red-400 transition-colors cursor-pointer"
              aria-label="Delete URL"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default URLList

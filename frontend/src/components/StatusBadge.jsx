function StatusBadge({ check }) {
  if (!check) {
    return (
      <span className="h-3 w-3 rounded-full bg-gray-500 shrink-0" title="Pending" />
    )
  }

  return (
    <span
      className={`h-3 w-3 rounded-full shrink-0 ${
        check.is_up ? 'bg-green-500' : 'bg-red-500'
      }`}
      title={check.is_up ? 'Up' : 'Down'}
    />
  )
}

export default StatusBadge

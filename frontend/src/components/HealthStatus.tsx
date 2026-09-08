import { useEffect, useState } from "react"
import { fetchHealth, type HealthResponse } from "../services/api"

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data)
        setError(false)
      })
      .catch(() => {
        setError(true)
      })
  }, [])

  if (error) {
    return (
      <span className="rounded-full px-3 py-1 text-sm ring-2 ring-red-500">
        API: unreachable
      </span>
    )
  }

  if (!health) {
    return (
      <span className="rounded-full px-3 py-1 text-sm ring-2 ring-amber-500">
        Checking…
      </span>
    )
  }

  const healthy = health.status === "ok" && health.db === "ok"

  return (
    <span
      className={`rounded-full px-3 py-1 text-sm ring-2 ${
        healthy ? "ring-emerald-500" : "ring-amber-500"
      }`}
    >
      API: {health.status} · DB: {health.db}
    </span>
  )
}
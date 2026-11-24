import { useEffect, useState } from "react"

import {
  fetchAlerts,
  fetchLocationConfig,
  fetchLocations,
  type AlertDto,
  type LocationConfigDto,
} from "../../services/api"


const POLL_INTERVAL_MS = 5000   // live push replaces this in Phase 12

const severityColors: Record<string, string> = {
  info: "bg-blue-100 text-blue-700",
  warning: "bg-amber-100 text-amber-700",
  critical: "bg-red-100 text-red-700",
}


export default function EventFeed() {
  const [locations, setLocations] = useState<LocationConfigDto[]>([])
  const [locationId, setLocationId] = useState("")
  const [zoneId, setZoneId] = useState("")
  const [onlyActive, setOnlyActive] = useState(true)
  const [alerts, setAlerts] = useState<AlertDto[]>([])
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Load locations + zones once, for the filter dropdowns
  useEffect(() => {
    async function loadLocations() {
      try {
        const list = await fetchLocations()
        const configs = await Promise.all(list.map((l) => fetchLocationConfig(l.id)))
        setLocations(configs)
      } catch {
        setError("Failed to load locations")
      }
    }
    void loadLocations()
  }, [])

  // Poll alerts every few seconds; restart when filters change
  useEffect(() => {
    async function loadAlerts() {
      try {
        const data = await fetchAlerts({
          status: onlyActive ? "active" : undefined,
          locationId: locationId || undefined,
          zoneId: zoneId || undefined,
        })
        setAlerts(data)
        setLastUpdated(new Date())
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load alerts")
      }
    }

    void loadAlerts()
    const timer = setInterval(() => void loadAlerts(), POLL_INTERVAL_MS)
    return () => clearInterval(timer)
  }, [locationId, zoneId, onlyActive])

  const zones = locations.find((c) => c.location.id === locationId)?.zones ?? []

  function zoneName(id: string | null) {
    if (!id) return "—"
    for (const config of locations) {
      const zone = config.zones.find((z) => z.id === id)
      if (zone) return `${config.location.name} — ${zone.name}`
    }
    return id.slice(0, 8)
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500">
        Refreshes every {POLL_INTERVAL_MS / 1000} seconds (live push comes in Phase 12).
        {lastUpdated && ` Last update: ${lastUpdated.toLocaleTimeString()}.`}
      </p>

      <div className="flex flex-wrap items-center gap-2">
        <select
          value={locationId}
          onChange={(e) => {
            setLocationId(e.target.value)
            setZoneId("")            // zone belongs to the old location
          }}
          className="rounded border p-2 text-sm"
        >
          <option value="">All locations</option>
          {locations.map((c) => (
            <option key={c.location.id} value={c.location.id}>
              {c.location.name}
            </option>
          ))}
        </select>

        <select
          value={zoneId}
          onChange={(e) => setZoneId(e.target.value)}
          disabled={!locationId}
          className="rounded border p-2 text-sm disabled:opacity-50"
        >
          <option value="">All zones</option>
          {zones.map((z) => (
            <option key={z.id} value={z.id}>
              {z.name}
            </option>
          ))}
        </select>

        <label className="flex items-center gap-1 text-sm">
          <input
            type="checkbox"
            checked={onlyActive}
            onChange={(e) => setOnlyActive(e.target.checked)}
          />
          Active only
        </label>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {alerts.length === 0 ? (
        <p className="rounded border border-dashed p-6 text-center text-sm text-slate-500">
          No alerts. Everything looks fine in the greenhouse.
        </p>
      ) : (
        <ul className="space-y-2">
          {alerts.map((alert) => (
            <li key={alert.id} className="rounded border p-3">
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`rounded px-2 py-0.5 text-xs font-semibold ${severityColors[alert.severity] ?? ""}`}
                >
                  {alert.severity}
                </span>
                <span className="text-xs text-slate-500">{alert.event_type}</span>
                <span className="ml-auto text-xs text-slate-500">
                  {new Date(alert.created_at).toLocaleString()}
                </span>
              </div>
              <p className="mt-1 text-sm">{alert.message}</p>
              <p className="mt-1 text-xs text-slate-500">Zone: {zoneName(alert.zone_id)}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
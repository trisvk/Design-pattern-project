import { useEffect, useState } from "react"

import {
  fetchCommandHistory,
  fetchDevices,
  submitCommand,
  type CommandLogDto,
  type DeviceDto,
} from "../../services/api"


const COMMANDS = [
  { type: "start_pump", label: "Start pump" },
  { type: "stop_pump", label: "Stop pump" },
  { type: "set_light_level", label: "Set light level" },
]

const statusColors: Record<string, string> = {
  success: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
  rejected: "bg-amber-100 text-amber-700",
}


export default function CommandPanel() {
  const [actuators, setActuators] = useState<DeviceDto[]>([])
  const [history, setHistory] = useState<CommandLogDto[]>([])
  const [levels, setLevels] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(false)
  const [lastResult, setLastResult] = useState<CommandLogDto | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    try {
      setLoading(true)
      setError(null)
      const [devices, rows] = await Promise.all([
        fetchDevices({ role: "actuator" }),
        fetchCommandHistory(50),
      ])
      setActuators(devices)
      setHistory(rows)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function handleCommand(device: DeviceDto, commandType: string) {
    try {
      setLoading(true)
      setError(null)
      const payload =
        commandType === "set_light_level" ? { level: levels[device.id] ?? 1 } : {}
      const result = await submitCommand(device.id, commandType, payload)
      setLastResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Command failed")
    } finally {
      await load()   // refresh allowed_commands + history
    }
  }

  return (
    <div className="space-y-6">
      {error && <p className="text-sm text-red-600">{error}</p>}

      {lastResult && (
        <p className="text-sm">
          Last command <strong>{lastResult.command_type}</strong>:{" "}
          <span className={`rounded px-2 py-0.5 text-xs font-semibold ${statusColors[lastResult.status]}`}>
            {lastResult.status}
          </span>
          {lastResult.error_message && (
            <span className="ml-2 text-slate-600">{lastResult.error_message}</span>
          )}
        </p>
      )}

      <div className="grid gap-3 md:grid-cols-2">
        {actuators.length === 0 && (
          <p className="text-sm text-slate-500">No actuators. Provision a device family first.</p>
        )}

        {actuators.map((device) => (
          <div key={device.id} className="rounded border p-4">
            <div className="flex items-center justify-between">
              <strong>{device.display_name ?? device.device_type}</strong>
              <span className="rounded border px-2 py-0.5 text-xs font-semibold">
                {device.state ?? "unknown"}
              </span>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-2">
              {COMMANDS.map((cmd) => {
                const allowed = device.allowed_commands.includes(cmd.type)
                return (
                  <button
                    key={cmd.type}
                    type="button"
                    disabled={loading || !allowed}
                    title={allowed ? "" : `Not allowed in state "${device.state}"`}
                    onClick={() => void handleCommand(device, cmd.type)}
                    className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white disabled:cursor-not-allowed disabled:bg-slate-300"
                  >
                    {cmd.label}
                  </button>
                )
              })}

              <input
                type="number"
                min={0}
                max={100}
                value={levels[device.id] ?? 1}
                onChange={(e) =>
                  setLevels({ ...levels, [device.id]: Number(e.target.value) })
                }
                className="w-20 rounded border p-1.5 text-sm"
                title="Light level"
              />
            </div>
          </div>
        ))}
      </div>

      <div>
        <h4 className="mb-2 font-semibold">Command history</h4>
        {history.length === 0 ? (
          <p className="rounded border border-dashed p-6 text-center text-sm text-slate-500">
            No commands yet.
          </p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="border-b text-xs uppercase text-slate-500">
              <tr>
                <th className="py-2">Time</th>
                <th>Device</th>
                <th>Command</th>
                <th>Status</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {history.map((row) => (
                <tr key={row.id} className="border-b">
                  <td className="py-2">{new Date(row.created_at).toLocaleString()}</td>
                  <td>
                    {actuators.find((d) => d.id === row.device_id)?.display_name ??
                      row.device_id.slice(0, 8)}
                  </td>
                  <td>{row.command_type}</td>
                  <td>
                    <span className={`rounded px-2 py-0.5 text-xs font-semibold ${statusColors[row.status]}`}>
                      {row.status}
                    </span>
                  </td>
                  <td>{row.error_message ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
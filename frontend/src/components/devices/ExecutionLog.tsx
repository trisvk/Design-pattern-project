import { useEffect, useState } from "react"

import {
  applyActuatorDemo,
  fetchDevices,
  fetchExecutions,
  type DeviceDto,
  type ExecutionDto,
} from "../../services/api"


export default function ExecutionLog() {
  const [actuators, setActuators] = useState<DeviceDto[]>([])
  const [executions, setExecutions] = useState<ExecutionDto[]>([])
  const [deviceId, setDeviceId] = useState("")
  const [command, setCommand] = useState("start_pump")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    try {
      setLoading(true)
      setError(null)
      const devices = await fetchDevices({ role: "actuator" })
      setActuators(devices)
      if (!deviceId && devices.length > 0) setDeviceId(devices[0].id)
      setExecutions(await fetchExecutions(20))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function handleApply() {
    setError(null)
    try {
      await applyActuatorDemo(deviceId, command)
    } catch (err) {
      // 409 = blocked, but the backend still logged the row
      setError(err instanceof Error ? `Blocked: ${err.message}` : "Apply failed")
    }
    setExecutions(await fetchExecutions(20))
  }

  function deviceName(id: string) {
    const d = actuators.find((a) => a.id === id)
    return d ? d.display_name ?? d.device_type : id.slice(0, 8)
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900">
        Commands are not validated in this phase: any command succeeds until the
        actuator has been <code>running</code> for 30 minutes. A success row has
        policy <code>logging</code> and an empty message. A blocked row shows{" "}
        <code>Max run time exceeded</code> with policies <code>maxRunTime, logging</code>.
      </div>

      <div className="flex flex-wrap items-end gap-2">
        <select
          value={deviceId}
          onChange={(e) => setDeviceId(e.target.value)}
          className="rounded border p-2 text-sm"
        >
          {actuators.map((d) => (
            <option key={d.id} value={d.id}>
              {d.display_name ?? d.device_type} ({d.state ?? "?"})
            </option>
          ))}
        </select>

        <input
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          className="rounded border p-2 text-sm"
        />

        <button
          type="button"
          onClick={() => void handleApply()}
          disabled={loading || !deviceId}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Apply
        </button>

        <button
          type="button"
          onClick={() => void load()}
          disabled={loading}
          className="rounded border px-4 py-2 text-sm hover:bg-slate-100"
        >
          Refresh
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {executions.length === 0 ? (
        <p className="rounded border border-dashed p-6 text-center text-sm text-slate-500">
          No executions yet.
        </p>
      ) : (
        <table className="w-full text-left text-sm">
          <thead className="border-b text-xs uppercase text-slate-500">
            <tr>
              <th className="py-2">Time</th>
              <th>Device</th>
              <th>Result</th>
              <th>Policies</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {executions.map((row) => (
              <tr key={row.id} className="border-b">
                <td className="py-2">{new Date(row.created_at).toLocaleString()}</td>
                <td>{deviceName(row.device_id)}</td>
                <td>
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-semibold ${
                      row.success
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {row.success ? "success" : "failed"}
                  </span>
                </td>
                <td>{row.policy_applied.join(", ")}</td>
                <td>{row.message ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
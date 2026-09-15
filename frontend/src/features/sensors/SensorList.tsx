import { useEffect, useState } from "react"
import {
  createSensor,
  fetchSensors,
  type SensorDto,
} from "../../services/api"

export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  async function loadSensors() {
    try {
      const data = await fetchSensors()
      setSensors(data)
      setError("")
    } catch {
      setError("Could not load sensors.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSensors()
  }, [])

  async function handleCreate(type: "moisture" | "light") {
    try {
      const sensor = await createSensor(type)
      setSensors((current) => [...current, sensor])
      setError("")
    } catch {
      setError("Could not create sensor.")
    }
  }

  return (
    <div>
      <div className="mb-4 flex gap-2">
        <button
          onClick={() => handleCreate("moisture")}
          className="rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white"
        >
          Add moisture
        </button>

        <button
          onClick={() => handleCreate("light")}
          className="rounded-lg bg-amber-500 px-3 py-2 text-sm text-white"
        >
          Add light
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 p-3 text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <p>Loading sensors...</p>
      ) : sensors.length === 0 ? (
        <p className="text-slate-500">No sensors yet.</p>
      ) : (
        <div className="space-y-3">
          {sensors.map((sensor) => (
            <div
              key={sensor.id}
              className="rounded-lg border border-slate-200 p-3"
            >
              <p className="font-medium">
                {sensor.display_name ?? "Unnamed sensor"}
              </p>

              <p className="text-sm text-slate-500">
                {sensor.device_type}
              </p>

              <pre className="mt-2 overflow-auto text-xs">
                {JSON.stringify(sensor.default_config, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
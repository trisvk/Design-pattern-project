import { useEffect, useState } from "react"
import {
  createSensor,
  fetchSensorReadings,
  fetchSensors,
  readSensorNow,
  updateSampling,
  type ReadingDto,
  type SensorDto,
} from "../../services/api"


type SensorCardProps = {
  sensor: SensorDto
}


function SensorCard({ sensor }: SensorCardProps) {
  const [reading, setReading] =
    useState<ReadingDto | null>(null)

  const [intervalSeconds, setIntervalSeconds] =
    useState(300)

  const [trackingEnabled, setTrackingEnabled] =
    useState(true)

  const [readingLoading, setReadingLoading] =
    useState(false)

  const [saving, setSaving] =
    useState(false)

  const [error, setError] =
    useState("")


  async function loadLatestReading() {
    try {
      const readings = await fetchSensorReadings(
        sensor.id,
        1,
      )

      setReading(readings[0] ?? null)
    } catch {
      setError("Could not load latest reading.")
    }
  }


  useEffect(() => {
    loadLatestReading()

    // Phase 12 replaces this polling with WebSocket.
    const timer = window.setInterval(
      loadLatestReading,
      5000,
    )

    return () => {
      window.clearInterval(timer)
    }
  }, [sensor.id])


  async function handleReadNow() {
    try {
      setReadingLoading(true)
      setError("")

      const result = await readSensorNow(
        sensor.id,
      )

      setReading(result)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not read sensor.",
      )
    } finally {
      setReadingLoading(false)
    }
  }


  async function handleSamplingSave() {
    try {
      setSaving(true)
      setError("")

      const result = await updateSampling(
        sensor.id,
        {
          sampling_interval_seconds:
            intervalSeconds,
          tracking_enabled:
            trackingEnabled,
        },
      )

      setIntervalSeconds(
        result.sampling_interval_seconds,
      )

      setTrackingEnabled(
        result.tracking_enabled,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not update sampling.",
      )
    } finally {
      setSaving(false)
    }
  }


  return (
    <div className="rounded-lg border border-slate-200 p-4">
      <p className="font-medium">
        {sensor.display_name ?? "Unnamed sensor"}
      </p>

      <p className="text-sm text-slate-500">
        {sensor.device_type}
      </p>

      <div className="mt-3">
        {reading ? (
          <>
            <p className="text-xl font-semibold">
              {reading.value.toFixed(2)}{" "}
              {reading.unit}
            </p>

            <span className="mt-1 inline-block rounded-full bg-slate-100 px-2 py-1 text-xs">
              {reading.source}
            </span>

            <p className="mt-1 text-xs text-slate-400">
              {new Date(
                reading.recorded_at,
              ).toLocaleString()}
            </p>
          </>
        ) : (
          <p className="text-sm text-slate-500">
            No readings yet.
          </p>
        )}
      </div>

      {sensor.default_config.protocol !== "gpio-stub" && (
        <button
          onClick={handleReadNow}
          disabled={readingLoading}
          className="mt-3 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white disabled:opacity-50"
        >
          {readingLoading
            ? "Reading..."
            : "Read now"}
        </button>
      )}

      <div className="mt-4 border-t pt-3">
        <label className="block text-sm">
          Sampling interval (seconds)
        </label>

        <input
          type="number"
          min="5"
          value={intervalSeconds}
          onChange={(event) =>
            setIntervalSeconds(
              Number(event.target.value),
            )
          }
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        />

        <label className="mt-3 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={trackingEnabled}
            onChange={(event) =>
              setTrackingEnabled(
                event.target.checked,
              )
            }
          />

          Tracking enabled
        </label>

        <button
          onClick={handleSamplingSave}
          disabled={saving}
          className="mt-3 rounded-lg bg-slate-700 px-3 py-2 text-sm text-white disabled:opacity-50"
        >
          {saving
            ? "Saving..."
            : "Save sampling"}
        </button>
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  )
}


export default function SensorList() {
  const [sensors, setSensors] =
    useState<SensorDto[]>([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState("")


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


  async function handleCreate(
    type: "moisture" | "light",
  ) {
    try {
      const sensor = await createSensor(type)

      setSensors((current) => [
        ...current,
        sensor,
      ])

      setError("")
    } catch {
      setError("Could not create sensor.")
    }
  }


  return (
    <div>
      <div className="mb-4 flex gap-2">
        <button
          onClick={() =>
            handleCreate("moisture")
          }
          className="rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white"
        >
          Add moisture
        </button>

        <button
          onClick={() =>
            handleCreate("light")
          }
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
        <p className="text-slate-500">
          No sensors yet.
        </p>
      ) : (
        <div className="space-y-3">
          {sensors.map((sensor) => (
            <SensorCard
              key={sensor.id}
              sensor={sensor}
            />
          ))}
        </div>
      )}
    </div>
  )
}
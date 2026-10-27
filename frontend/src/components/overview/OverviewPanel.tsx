import { useEffect, useState } from "react"
import {
  fetchLocations,
  fetchLocationOverview,
  type LocationDto,
  type LocationOverviewDto,
} from "../../services/api"

export default function OverviewPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([])
  const [locationId, setLocationId] = useState("")
  const [overview, setOverview] =
    useState<LocationOverviewDto | null>(null)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [refreshCount, setRefreshCount] = useState(0)

  useEffect(() => {
    let active = true

    async function loadLocations() {
      try {
        const data = await fetchLocations()

        if (!active) return

        setLocations(data)

        if (data.length > 0) {
          setLocationId(data[0].id)
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load locations",
          )
        }
      }
    }

    void loadLocations()

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!locationId) {
      setOverview(null)
      return
    }

    let active = true

    setLoading(true)
    setError("")
    setOverview(null)

    async function loadOverview() {
      try {
        const data = await fetchLocationOverview(locationId)

        if (active) {
          setOverview(data)
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load overview",
          )
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadOverview()

    return () => {
      active = false
    }
  }, [locationId, refreshCount])

  return (
    <div className="space-y-4 text-sm">
      <div className="flex flex-wrap items-end gap-3">
        <label className="flex min-w-0 flex-1 flex-col gap-1">
          <span className="font-medium">Location</span>

          <select
            value={locationId}
            onChange={(event) =>
              setLocationId(event.target.value)
            }
            className="w-full rounded-lg border border-slate-300 p-2"
          >
            {locations.length === 0 && (
              <option value="">No locations available</option>
            )}

            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          onClick={() => setRefreshCount((count) => count + 1)}
          disabled={!locationId || loading}
          className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      {loading && (
        <p className="text-slate-500">Loading overview...</p>
      )}

      {error && (
        <p className="rounded-lg bg-red-50 p-3 text-red-700">
          {error}
        </p>
      )}

      {overview && (
        <div className="space-y-4">
          <h4 className="text-lg font-semibold">
            {overview.location.name}
          </h4>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg bg-blue-50 p-4">
              <p className="text-slate-600">Assigned Sensors</p>
              <p className="text-2xl font-bold text-blue-700">
                {overview.device_counts.sensor}
              </p>
            </div>

            <div className="rounded-lg bg-green-50 p-4">
              <p className="text-slate-600">Assigned Actuators</p>
              <p className="text-2xl font-bold text-green-700">
                {overview.device_counts.actuator}
              </p>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 p-4">
            <h5 className="font-semibold">Automation</h5>

            <p className="mt-2">
              <strong>Strategy:</strong>{" "}
              {overview.strategy_key ?? "No strategy configured"}
            </p>

            {overview.last_recommendation ? (
              <div className="mt-2 space-y-1">
                <p>
                  <strong>Action:</strong>{" "}
                  <span className="font-semibold text-blue-700">
                    {overview.last_recommendation.action}
                  </span>
                </p>

                <p>
                  <strong>Reason:</strong>{" "}
                  {overview.last_recommendation.reason}
                </p>
              </div>
            ) : (
              <p className="mt-2 text-slate-500">
                No recommendation available.
              </p>
            )}
          </div>

          <h5 className="font-semibold">Zones</h5>

          {overview.zones.length === 0 && (
            <p className="text-slate-500">
              No zones configured.
            </p>
          )}

          {overview.zones.map((zone) => (
            <div
              key={zone.id}
              className="rounded-lg border border-slate-200 p-4"
            >
              <h6 className="font-semibold">{zone.name}</h6>

              <p className="mt-2 text-slate-600">
                Moisture thresholds:{" "}
                {zone.moisture_threshold_low} –{" "}
                {zone.moisture_threshold_high}
              </p>

              {zone.devices.length === 0 ? (
                <p className="mt-3 text-slate-500">
                  No assigned devices.
                </p>
              ) : (
                <div className="mt-3 space-y-3">
                  {zone.devices.map((device) => {
                    const reading = zone.latest_readings.find(
                      (item) => item.device_id === device.id,
                    )

                    return (
                      <div
                        key={device.id}
                        className="rounded-lg bg-slate-50 p-3"
                      >
                        <p className="font-medium">
                          {device.display_name ||
                            device.device_type}
                        </p>

                        <p className="text-slate-600">
                          Role: {device.role}
                        </p>

                        <p className="text-slate-600">
                          Type: {device.device_type}
                        </p>

                        {reading ? (
                          <div className="mt-2 space-y-1">
                            <p>
                              <strong>Latest reading:</strong>{" "}
                              {reading.value} {reading.unit}
                            </p>

                            <p>
                              <strong>Tracking:</strong>{" "}
                              {reading.tracking_enabled
                                ? "Enabled"
                                : "Disabled"}
                            </p>

                            <p>
                              <strong>Sampling:</strong>{" "}
                              {reading.sampling_interval_seconds} seconds
                            </p>

                            <p className="text-xs text-slate-500">
                              Recorded:{" "}
                              {new Date(
                                reading.recorded_at,
                              ).toLocaleString()}
                            </p>
                          </div>
                        ) : (
                          <p className="mt-2 text-slate-500">
                            No reading available.
                          </p>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

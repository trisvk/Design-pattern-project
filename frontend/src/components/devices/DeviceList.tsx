
import { useEffect, useState } from "react"

import {
  assignDeviceToZone,
  fetchDevices,
  fetchLocationConfig,
  fetchLocations,
  fetchZoneDevices,
  provisionDeviceFamily,
  type DeviceDto,
  type DeviceFamily,
  type LocationConfigDto,
} from "../../services/api"

import DeviceFamilySwitcher from "./DeviceFamilySwitcher"


const stateColors: Record<string, string> = {
  idle: "bg-slate-100 text-slate-700 border-slate-300",
  running: "bg-emerald-100 text-emerald-700 border-emerald-300",
  error: "bg-red-100 text-red-700 border-red-300",
  maintenance: "bg-amber-100 text-amber-700 border-amber-300",
  off: "bg-gray-100 text-gray-700 border-gray-300",
}


type Assignment = {
  zoneId: string
  label: string
}


export default function DeviceList() {
  const [family, setFamily] =
    useState<DeviceFamily>("simulation")

  const [devices, setDevices] =
    useState<DeviceDto[]>([])

  const [locations, setLocations] =
    useState<LocationConfigDto[]>([])

  const [assignments, setAssignments] =
    useState<Record<string, Assignment>>({})

  const [loading, setLoading] = useState(false)

  const [error, setError] =
    useState<string | null>(null)


  async function loadZoneData() {
    const savedLocations = await fetchLocations()

    const configs = await Promise.all(
      savedLocations.map((location) =>
        fetchLocationConfig(location.id),
      ),
    )

    setLocations(configs)

    const assignmentMap: Record<string, Assignment> = {}

    await Promise.all(
      configs.flatMap((config) =>
        config.zones.map(async (zone) => {
          const zoneDevices = await fetchZoneDevices(
            config.location.id,
            zone.id,
          )

          for (const device of zoneDevices) {
            assignmentMap[device.id] = {
              zoneId: zone.id,
              label: `${config.location.name} — ${zone.name}`,
            }
          }
        }),
      ),
    )

    setAssignments(assignmentMap)
  }


  async function loadDevices(selectedFamily: DeviceFamily) {
    try {
      setLoading(true)
      setError(null)

      const data = await fetchDevices({
        family: selectedFamily,
      })

      console.log("Phase 8 devices:", data)

      setDevices(data)

      await loadZoneData()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load devices",
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    void loadDevices(family)
  }, [family])


  async function handleProvision() {
    try {
      setLoading(true)
      setError(null)

      await provisionDeviceFamily(family)

      await loadDevices(family)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to provision device family",
      )
    } finally {
      setLoading(false)
    }
  }


  async function handleZoneChange(
    deviceId: string,
    zoneId: string,
  ) {
    try {
      setLoading(true)
      setError(null)

      await assignDeviceToZone(
        deviceId,
        zoneId || null,
      )

      await loadZoneData()

      window.dispatchEvent(
        new Event("device-zone-changed"),
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to assign zone",
      )
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="space-y-4">
      <DeviceFamilySwitcher
        family={family}
        onChange={setFamily}
      />

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={handleProvision}
          disabled={loading}
          className="rounded border px-4 py-2 disabled:opacity-50"
        >
          Provision {family}
        </button>

        <button
          type="button"
          onClick={() => void loadDevices(family)}
          disabled={loading}
          className="rounded border px-4 py-2 hover:bg-slate-100 disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      {error && (
        <p className="text-sm text-red-600">
          {error}
        </p>
      )}

      {loading && (
        <p className="text-sm text-slate-500">
          Loading...
        </p>
      )}

      <div className="space-y-3">
        {devices.map((device) => {
          const assignment = assignments[device.id]

          return (
            <div
              key={device.id}
              className="rounded border p-4"
            >
              <div className="flex flex-wrap items-center gap-2">
                <strong>
                  {device.display_name ?? "Unnamed device"}
                </strong>

                <span className="rounded bg-slate-100 px-2 py-1 text-xs">
                  {device.role}
                </span>

                <span className="rounded border px-2 py-1 text-xs">
                  {device.device_family}
                </span>

                {device.role === "actuator" && (
                  <span
                    title={
                      device.allowed_commands.length > 0
                        ? `Allowed commands: ${device.allowed_commands.join(", ")}`
                        : "No commands available"
                    }
                    className={`cursor-help rounded border px-3 py-1 text-xs font-semibold ${
                      stateColors[device.state ?? ""] ??
                      "bg-gray-100 text-gray-600 border-gray-300"
                    }`}
                  >
                    {device.state ?? "Unknown"}
                  </span>
                )}
              </div>

              <p className="mt-2 text-sm">
                {device.device_type}
              </p>

              <pre className="mt-2 overflow-auto text-xs">
                {JSON.stringify(
                  device.default_config,
                  null,
                  2,
                )}
              </pre>

              <div className="mt-4">
                <label className="mb-1 block text-sm font-medium">
                  Zone
                </label>

                <select
                  value={assignment?.zoneId ?? ""}
                  disabled={loading}
                  onChange={(event) =>
                    void handleZoneChange(
                      device.id,
                      event.target.value,
                    )
                  }
                  className="w-full rounded border p-2 text-sm"
                >
                  <option value="">
                    Unassigned
                  </option>

                  {locations.map((config) => (
                    <optgroup
                      key={config.location.id}
                      label={config.location.name}
                    >
                      {config.zones.map((zone) => (
                        <option
                          key={zone.id}
                          value={zone.id}
                        >
                          {config.location.name} — {zone.name}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>

                <p className="mt-1 text-xs text-slate-500">
                  Current:{" "}
                  {assignment?.label ?? "Unassigned"}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

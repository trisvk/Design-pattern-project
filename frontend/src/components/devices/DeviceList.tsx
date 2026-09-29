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

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)


  async function loadZoneData() {
    const savedLocations =
      await fetchLocations()

    const configs =
      await Promise.all(
        savedLocations.map((location) =>
          fetchLocationConfig(location.id),
        ),
      )

    setLocations(configs)

    const assignmentMap:
      Record<string, Assignment> = {}

    await Promise.all(
      configs.flatMap((config) =>
        config.zones.map(async (zone) => {
          const zoneDevices =
            await fetchZoneDevices(
              config.location.id,
              zone.id,
            )

          for (const device of zoneDevices) {
            assignmentMap[device.id] = {
              zoneId: zone.id,
              label:
                `${config.location.name} — ${zone.name}`,
            }
          }
        }),
      ),
    )

    setAssignments(assignmentMap)
  }


  async function loadDevices(
    selectedFamily: DeviceFamily,
  ) {
    try {
      setLoading(true)
      setError(null)

      const data =
        await fetchDevices({
          family: selectedFamily,
        })

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

      <button
        type="button"
        onClick={handleProvision}
        disabled={loading}
        className="rounded border px-4 py-2 disabled:opacity-50"
      >
        Provision {family}
      </button>

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
          const assignment =
            assignments[device.id]

          return (
            <div
              key={device.id}
              className="rounded border p-4"
            >
              <div className="flex flex-wrap items-center gap-2">
                <strong>
                  {device.display_name ??
                    "Unnamed device"}
                </strong>

                <span className="rounded bg-slate-100 px-2 py-1 text-xs">
                  {device.role}
                </span>

                <span className="rounded border px-2 py-1 text-xs">
                  {device.device_family}
                </span>
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
                  value={
                    assignment?.zoneId ?? ""
                  }
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

                  {locations.map(
                    (config) => (
                      <optgroup
                        key={
                          config.location.id
                        }
                        label={
                          config.location.name
                        }
                      >
                        {config.zones.map(
                          (zone) => (
                            <option
                              key={zone.id}
                              value={zone.id}
                            >
                              {
                                config.location
                                  .name
                              }{" "}
                              — {zone.name}
                            </option>
                          ),
                        )}
                      </optgroup>
                    ),
                  )}
                </select>

                <p className="mt-1 text-xs text-slate-500">
                  Current:{" "}
                  {assignment?.label ??
                    "Unassigned"}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
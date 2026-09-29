import { useEffect, useState } from "react"

import {
  addZone,
  createLocationConfig,
  deleteLocation,
  deleteZone,
  fetchLocationConfig,
  fetchLocations,
  fetchZoneDevices,
  updateZone,
  type DeviceDto,
  type LocationConfigDto,
  type LocationDto,
  type ZoneDto,
} from "../../services/api"


type ZoneForm = {
  name: string
  low: string
  high: string
  watering: string
}


function scheduleToTime(
  schedule: Record<string, unknown>,
): string {
  const watering = schedule.watering

  return typeof watering === "string"
    ? watering
    : ""
}


function validateZone(
  form: ZoneForm,
): string | null {
  if (!form.name.trim()) {
    return "Zone name is required."
  }

  const low = Number(form.low)
  const high = Number(form.high)

  if (
    Number.isNaN(low) ||
    Number.isNaN(high) ||
    low < 0 ||
    high > 1 ||
    low >= high
  ) {
    return (
      "Thresholds must be between 0 and 1, " +
      "and low must be lower than high."
    )
  }

  return null
}


export default function LocationConfigWizard() {
  const [locations, setLocations] =
    useState<LocationDto[]>([])

  const [selectedConfig, setSelectedConfig] =
    useState<LocationConfigDto | null>(null)

  const [zoneDevices, setZoneDevices] =
    useState<Record<string, DeviceDto[]>>({})

  // Create location
  const [locationName, setLocationName] =
    useState("")

  const [zoneName, setZoneName] =
    useState("")

  const [low, setLow] =
    useState("0.2")

  const [high, setHigh] =
    useState("0.5")

  const [watering, setWatering] =
    useState("08:00")

  // Add zone
  const [newZone, setNewZone] =
    useState<ZoneForm>({
      name: "",
      low: "0.2",
      high: "0.5",
      watering: "08:00",
    })

  // Edit zone
  const [editingZoneId, setEditingZoneId] =
    useState<string | null>(null)

  const [editZone, setEditZone] =
    useState<ZoneForm>({
      name: "",
      low: "",
      high: "",
      watering: "",
    })

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  const [success, setSuccess] =
    useState<string | null>(null)


  async function loadLocations() {
    try {
      setError(null)

      const data = await fetchLocations()

      setLocations(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load locations",
      )
    }
  }


  async function reloadSelectedLocation(
    locationId: string,
  ) {
    const config =
      await fetchLocationConfig(locationId)

    setSelectedConfig(config)

    const deviceEntries =
      await Promise.all(
        config.zones.map(async (zone) => {
          const devices =
            await fetchZoneDevices(
              locationId,
              zone.id,
            )

          return [
            zone.id,
            devices,
          ] as const
        }),
      )

    setZoneDevices(
      Object.fromEntries(deviceEntries),
    )
  }


  useEffect(() => {
    void loadLocations()
  }, [])


  useEffect(() => {
    function handleDeviceZoneChanged() {
      if (selectedConfig) {
        void reloadSelectedLocation(
          selectedConfig.location.id,
        )
      }
    }

    window.addEventListener(
      "device-zone-changed",
      handleDeviceZoneChanged,
    )

    return () => {
      window.removeEventListener(
        "device-zone-changed",
        handleDeviceZoneChanged,
      )
    }
  }, [selectedConfig])


  async function handleSelect(
    locationId: string,
  ) {
    if (!locationId) {
      setSelectedConfig(null)
      setEditingZoneId(null)
      setZoneDevices({})
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSuccess(null)
      setEditingZoneId(null)

      await reloadSelectedLocation(
        locationId,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load configuration",
      )
    } finally {
      setLoading(false)
    }
  }


  async function handleCreate() {
    setError(null)
    setSuccess(null)

    if (!locationName.trim()) {
      setError(
        "Location name is required.",
      )
      return
    }

    const validationError =
      validateZone({
        name: zoneName,
        low,
        high,
        watering,
      })

    if (validationError) {
      setError(validationError)
      return
    }

    try {
      setLoading(true)

      const created =
        await createLocationConfig({
          location_name:
            locationName.trim(),

          zones: [
            {
              name: zoneName.trim(),

              moisture_threshold_low:
                Number(low),

              moisture_threshold_high:
                Number(high),

              schedule: watering
                ? { watering }
                : {},
            },
          ],
        })

      await loadLocations()

      await reloadSelectedLocation(
        created.location.id,
      )

      setLocationName("")
      setZoneName("")
      setLow("0.2")
      setHigh("0.5")
      setWatering("08:00")

      setSuccess(
        "Location created successfully.",
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create location",
      )
    } finally {
      setLoading(false)
    }
  }


  async function handleDeleteLocation() {
    if (!selectedConfig) {
      return
    }

    const confirmed =
      window.confirm(
        `Delete "${selectedConfig.location.name}"?`,
      )

    if (!confirmed) {
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSuccess(null)

      await deleteLocation(
        selectedConfig.location.id,
      )

      setSelectedConfig(null)
      setEditingZoneId(null)
      setZoneDevices({})

      await loadLocations()

      window.dispatchEvent(
        new Event(
          "location-config-changed",
        ),
      )

      setSuccess(
        "Location deleted successfully.",
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete location",
      )
    } finally {
      setLoading(false)
    }
  }


  async function handleAddZone() {
    if (!selectedConfig) {
      return
    }

    setError(null)
    setSuccess(null)

    const validationError =
      validateZone(newZone)

    if (validationError) {
      setError(validationError)
      return
    }

    try {
      setLoading(true)

      await addZone(
        selectedConfig.location.id,
        {
          name: newZone.name.trim(),

          moisture_threshold_low:
            Number(newZone.low),

          moisture_threshold_high:
            Number(newZone.high),

          schedule: newZone.watering
            ? {
                watering:
                  newZone.watering,
              }
            : {},
        },
      )

      await reloadSelectedLocation(
        selectedConfig.location.id,
      )

      setNewZone({
        name: "",
        low: "0.2",
        high: "0.5",
        watering: "08:00",
      })

      window.dispatchEvent(
        new Event(
          "location-config-changed",
        ),
      )

      setSuccess(
        "Zone added successfully.",
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to add zone",
      )
    } finally {
      setLoading(false)
    }
  }


  function startEditing(
    zone: ZoneDto,
  ) {
    setError(null)
    setSuccess(null)

    setEditingZoneId(zone.id)

    setEditZone({
      name: zone.name,

      low: String(
        zone.moisture_threshold_low,
      ),

      high: String(
        zone.moisture_threshold_high,
      ),

      watering:
        scheduleToTime(zone.schedule),
    })
  }


  async function handleUpdateZone(
    zoneId: string,
  ) {
    if (!selectedConfig) {
      return
    }

    setError(null)
    setSuccess(null)

    const validationError =
      validateZone(editZone)

    if (validationError) {
      setError(validationError)
      return
    }

    try {
      setLoading(true)

      await updateZone(
        selectedConfig.location.id,
        zoneId,
        {
          name:
            editZone.name.trim(),

          moisture_threshold_low:
            Number(editZone.low),

          moisture_threshold_high:
            Number(editZone.high),

          schedule:
            editZone.watering
              ? {
                  watering:
                    editZone.watering,
                }
              : {},
        },
      )

      await reloadSelectedLocation(
        selectedConfig.location.id,
      )

      setEditingZoneId(null)

      window.dispatchEvent(
        new Event(
          "location-config-changed",
        ),
      )

      setSuccess(
        "Zone updated successfully.",
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update zone",
      )
    } finally {
      setLoading(false)
    }
  }


  async function handleDeleteZone(
    zone: ZoneDto,
  ) {
    if (!selectedConfig) {
      return
    }

    const confirmed =
      window.confirm(
        `Delete zone "${zone.name}"?`,
      )

    if (!confirmed) {
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSuccess(null)

      await deleteZone(
        selectedConfig.location.id,
        zone.id,
      )

      await reloadSelectedLocation(
        selectedConfig.location.id,
      )

      setEditingZoneId(null)

      window.dispatchEvent(
        new Event(
          "location-config-changed",
        ),
      )

      setSuccess(
        "Zone deleted successfully.",
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete zone",
      )
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="space-y-6">
      {error && (
        <div className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {success && (
        <div className="rounded border border-green-300 bg-green-50 p-3 text-sm text-green-700">
          {success}
        </div>
      )}

      {/* CREATE LOCATION */}

      <div className="rounded border p-4">
        <h4 className="mb-3 font-semibold">
          Create location
        </h4>

        <div className="space-y-3">
          <input
            value={locationName}
            onChange={(event) =>
              setLocationName(
                event.target.value,
              )
            }
            placeholder="Location name"
            className="w-full rounded border p-2"
          />

          <input
            value={zoneName}
            onChange={(event) =>
              setZoneName(
                event.target.value,
              )
            }
            placeholder="First zone name"
            className="w-full rounded border p-2"
          />

          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={low}
              onChange={(event) =>
                setLow(
                  event.target.value,
                )
              }
              className="rounded border p-2"
            />

            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={high}
              onChange={(event) =>
                setHigh(
                  event.target.value,
                )
              }
              className="rounded border p-2"
            />
          </div>

          <input
            type="time"
            value={watering}
            onChange={(event) =>
              setWatering(
                event.target.value,
              )
            }
            className="w-full rounded border p-2"
          />

          <button
            type="button"
            onClick={handleCreate}
            disabled={loading}
            className="rounded bg-slate-900 px-4 py-2 text-white disabled:opacity-50"
          >
            Create location
          </button>
        </div>
      </div>

      {/* SAVED LOCATIONS */}

      <div className="rounded border p-4">
        <h4 className="mb-3 font-semibold">
          Saved locations
        </h4>

        {locations.length === 0 ? (
          <p className="text-sm text-slate-500">
            No saved locations.
          </p>
        ) : (
          <select
            value={
              selectedConfig
                ?.location.id ?? ""
            }
            onChange={(event) =>
              void handleSelect(
                event.target.value,
              )
            }
            className="w-full rounded border p-2"
          >
            <option value="">
              Select a location
            </option>

            {locations.map(
              (location) => (
                <option
                  key={location.id}
                  value={location.id}
                >
                  {location.name}
                </option>
              ),
            )}
          </select>
        )}
      </div>

      {/* SELECTED LOCATION */}

      {selectedConfig && (
        <div className="rounded border p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h4 className="font-semibold">
                {
                  selectedConfig
                    .location.name
                }
              </h4>

              <p className="mt-1 break-all text-xs text-slate-500">
                ID:{" "}
                {
                  selectedConfig
                    .location.id
                }
              </p>
            </div>

            <button
              type="button"
              onClick={
                handleDeleteLocation
              }
              disabled={loading}
              className="rounded border border-red-300 px-3 py-2 text-sm text-red-700 disabled:opacity-50"
            >
              Delete location
            </button>
          </div>

          {/* ADD ZONE */}

          <div className="mt-6 rounded bg-slate-50 p-3">
            <h5 className="mb-3 font-medium">
              Add zone
            </h5>

            <div className="space-y-2">
              <input
                value={newZone.name}
                onChange={(event) =>
                  setNewZone({
                    ...newZone,
                    name:
                      event.target.value,
                  })
                }
                placeholder="Zone name"
                className="w-full rounded border bg-white p-2"
              />

              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={newZone.low}
                  onChange={(event) =>
                    setNewZone({
                      ...newZone,
                      low:
                        event.target.value,
                    })
                  }
                  placeholder="Low"
                  className="rounded border bg-white p-2"
                />

                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={newZone.high}
                  onChange={(event) =>
                    setNewZone({
                      ...newZone,
                      high:
                        event.target.value,
                    })
                  }
                  placeholder="High"
                  className="rounded border bg-white p-2"
                />
              </div>

              <input
                type="time"
                value={
                  newZone.watering
                }
                onChange={(event) =>
                  setNewZone({
                    ...newZone,
                    watering:
                      event.target.value,
                  })
                }
                className="w-full rounded border bg-white p-2"
              />

              <button
                type="button"
                onClick={handleAddZone}
                disabled={loading}
                className="rounded bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-50"
              >
                Add zone
              </button>
            </div>
          </div>

          {/* ZONES */}

          <div className="mt-6 space-y-3">
            <h5 className="font-medium">
              Zones
            </h5>

            {selectedConfig.zones.map(
              (zone) => (
                <div
                  key={zone.id}
                  className="rounded border bg-white p-3"
                >
                  {editingZoneId ===
                  zone.id ? (
                    <div className="space-y-2">
                      <input
                        value={
                          editZone.name
                        }
                        onChange={(
                          event,
                        ) =>
                          setEditZone({
                            ...editZone,
                            name:
                              event
                                .target
                                .value,
                          })
                        }
                        className="w-full rounded border p-2"
                      />

                      <div className="grid grid-cols-2 gap-2">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          max="1"
                          value={
                            editZone.low
                          }
                          onChange={(
                            event,
                          ) =>
                            setEditZone({
                              ...editZone,
                              low:
                                event
                                  .target
                                  .value,
                            })
                          }
                          className="rounded border p-2"
                        />

                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          max="1"
                          value={
                            editZone.high
                          }
                          onChange={(
                            event,
                          ) =>
                            setEditZone({
                              ...editZone,
                              high:
                                event
                                  .target
                                  .value,
                            })
                          }
                          className="rounded border p-2"
                        />
                      </div>

                      <input
                        type="time"
                        value={
                          editZone.watering
                        }
                        onChange={(
                          event,
                        ) =>
                          setEditZone({
                            ...editZone,
                            watering:
                              event
                                .target
                                .value,
                          })
                        }
                        className="w-full rounded border p-2"
                      />

                      <div className="flex gap-2">
                        <button
                          type="button"
                          disabled={
                            loading
                          }
                          onClick={() =>
                            void handleUpdateZone(
                              zone.id,
                            )
                          }
                          className="rounded bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-50"
                        >
                          Save
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            setEditingZoneId(
                              null,
                            )
                          }
                          className="rounded bg-slate-200 px-3 py-2 text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <p className="font-medium">
                        {zone.name}
                      </p>

                      <p className="text-sm text-slate-600">
                        Moisture:{" "}
                        {
                          zone.moisture_threshold_low
                        }{" "}
                        –{" "}
                        {
                          zone.moisture_threshold_high
                        }
                      </p>

                      <p className="text-sm text-slate-600">
                        Watering:{" "}
                        {scheduleToTime(
                          zone.schedule,
                        ) || "Not set"}
                      </p>

                      <p className="mt-1 break-all text-xs text-slate-500">
                        Zone ID: {zone.id}
                      </p>

                      {/* DEVICES IN THIS ZONE */}

                      <div className="mt-3">
                        <p className="text-sm font-medium">
                          Devices
                        </p>

                        {(zoneDevices[
                          zone.id
                        ] ?? []).length ===
                        0 ? (
                          <p className="mt-1 text-sm text-slate-500">
                            No devices
                            assigned.
                          </p>
                        ) : (
                          <ul className="mt-1 space-y-1">
                            {(
                              zoneDevices[
                                zone.id
                              ] ?? []
                            ).map(
                              (device) => (
                                <li
                                  key={
                                    device.id
                                  }
                                  className="text-sm text-slate-700"
                                >
                                  •{" "}
                                  {device.display_name ??
                                    "Unnamed device"}{" "}
                                  <span className="text-slate-500">
                                    (
                                    {
                                      device.device_type
                                    }
                                    )
                                  </span>
                                </li>
                              ),
                            )}
                          </ul>
                        )}
                      </div>

                      <div className="mt-3 flex gap-2">
                        <button
                          type="button"
                          onClick={() =>
                            startEditing(
                              zone,
                            )
                          }
                          className="rounded bg-slate-200 px-3 py-2 text-sm"
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          disabled={
                            loading
                          }
                          onClick={() =>
                            void handleDeleteZone(
                              zone,
                            )
                          }
                          className="rounded border border-red-300 px-3 py-2 text-sm text-red-700 disabled:opacity-50"
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ),
            )}
          </div>
        </div>
      )}
    </div>
  )
}
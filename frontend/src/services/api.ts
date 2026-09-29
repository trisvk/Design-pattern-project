export type HealthResponse = {
  status: string
  db: "ok" | "fail"
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"


async function getApiError(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const data = await response.json()

    if (typeof data.detail === "string") {
      return data.detail
    }
  } catch {
    // Ignore JSON parsing errors.
  }

  return fallback
}


// =========================
// Health
// =========================

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error("Failed to fetch health status")
  }

  return response.json()
}


// =========================
// Sensors
// =========================

export type SensorDto = {
  id: string
  device_type: string
  display_name: string | null
  default_config: Record<string, unknown>
}

export async function fetchSensors(): Promise<SensorDto[]> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`)

  if (!response.ok) {
    throw new Error("Failed to fetch sensors")
  }

  return response.json()
}

export async function createSensor(
  type: string,
  displayName?: string,
): Promise<SensorDto> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      display_name: displayName ?? null,
    }),
  })

  if (!response.ok) {
    throw new Error("Failed to create sensor")
  }

  return response.json()
}


// =========================
// Devices
// =========================

export type DeviceFamily = "simulation" | "edge"

export interface DeviceDto {
  id: string
  device_type: string
  role: string
  device_family: DeviceFamily
  display_name: string | null
  default_config: Record<string, unknown>
}

type DeviceFilters = {
  family?: DeviceFamily
  role?: string
}

export async function fetchDevices(
  filters: DeviceFilters = {},
): Promise<DeviceDto[]> {
  const params = new URLSearchParams()

  if (filters.family) {
    params.set("family", filters.family)
  }

  if (filters.role) {
    params.set("role", filters.role)
  }

  const query = params.toString()

  const url = query
    ? `${API_BASE_URL}/api/devices?${query}`
    : `${API_BASE_URL}/api/devices`

  const response = await fetch(url)

  if (!response.ok) {
    throw new Error("Failed to fetch devices")
  }

  return response.json()
}

export async function provisionDeviceFamily(
  family: DeviceFamily,
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/provision?family=${encodeURIComponent(family)}`,
    {
      method: "POST",
    },
  )

  if (!response.ok) {
    throw new Error("Failed to provision device family")
  }

  return response.json()
}


// =========================
// Locations / Zones
// =========================

export interface LocationDto {
  id: string
  name: string
}

export interface ZoneDto {
  id: string
  location_id: string
  name: string
  moisture_threshold_low: number
  moisture_threshold_high: number
  schedule: Record<string, unknown>
}

export interface LocationConfigDto {
  location: LocationDto
  zones: ZoneDto[]
}

export interface ZoneRequest {
  name: string
  moisture_threshold_low: number
  moisture_threshold_high: number
  schedule?: Record<string, unknown>
}

export interface CreateLocationConfigRequest {
  location_name: string
  zones: ZoneRequest[]
}


// GET /api/locations
export async function fetchLocations(): Promise<LocationDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations`,
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to load locations",
      ),
    )
  }

  return response.json()
}


// POST /api/locations/config
export async function createLocationConfig(
  request: CreateLocationConfigRequest,
): Promise<LocationConfigDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/config`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to create location",
      ),
    )
  }

  return response.json()
}


// GET /api/locations/{location_id}/config
export async function fetchLocationConfig(
  locationId: string,
): Promise<LocationConfigDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/config`,
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to load location configuration",
      ),
    )
  }

  return response.json()
}


// DELETE /api/locations/{location_id}
export async function deleteLocation(
  locationId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}`,
    {
      method: "DELETE",
    },
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to delete location",
      ),
    )
  }
}


// POST /api/locations/{location_id}/zones
export async function addZone(
  locationId: string,
  request: ZoneRequest,
): Promise<ZoneDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to add zone",
      ),
    )
  }

  return response.json()
}


// PATCH /api/locations/{location_id}/zones/{zone_id}
export async function updateZone(
  locationId: string,
  zoneId: string,
  request: ZoneRequest,
): Promise<ZoneDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to update zone",
      ),
    )
  }

  return response.json()
}


// DELETE /api/locations/{location_id}/zones/{zone_id}
export async function deleteZone(
  locationId: string,
  zoneId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "DELETE",
    },
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to delete zone",
      ),
    )
  }
}


// =========================
// Zone device assignment
// =========================

// PATCH /api/devices/{id}/zone
export async function assignDeviceToZone(
  deviceId: string,
  zoneId: string | null,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/${deviceId}/zone`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        zone_id: zoneId,
      }),
    },
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to assign device",
      ),
    )
  }
}


// GET /api/locations/{location_id}/zones/{zone_id}/devices
export async function fetchZoneDevices(
  locationId: string,
  zoneId: string,
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}/devices`,
  )

  if (!response.ok) {
    throw new Error(
      await getApiError(
        response,
        "Failed to load zone devices",
      ),
    )
  }

  return response.json()
}
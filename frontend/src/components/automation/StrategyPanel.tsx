import { useEffect, useState } from "react"

import {
  evaluateAutomation,
  fetchLocations,
  saveAutomationStrategy,
  type LocationDto,
  type RecommendationDto,
  type StrategyKey,
} from "../../services/api"


export default function StrategyPanel() {
  const [locations, setLocations] = useState<
    LocationDto[]
  >([])

  const [locationId, setLocationId] =
    useState("")

  const [strategyKey, setStrategyKey] =
    useState<StrategyKey>("conservative")

  const [recommendation, setRecommendation] =
    useState<RecommendationDto | null>(null)

  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)


  useEffect(() => {
    async function loadLocations() {
      try {
        const data = await fetchLocations()

        setLocations(data)

        if (data.length > 0) {
          setLocationId(data[0].id)
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load locations",
        )
      }
    }

    void loadLocations()
  }, [])


  async function handleSave() {
    if (!locationId) {
      setError("Select a location first")
      return
    }

    setLoading(true)
    setError("")
    setMessage("")

    try {
      const result =
        await saveAutomationStrategy(
          locationId,
          strategyKey,
        )

      setMessage(
        `Saved strategy: ${result.strategy_key}`,
      )

      setRecommendation(null)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to save strategy",
      )
    } finally {
      setLoading(false)
    }
  }


  async function handleEvaluate() {
    if (!locationId) {
      setError("Select a location first")
      return
    }

    setLoading(true)
    setError("")
    setMessage("")

    try {
      const result =
        await evaluateAutomation(locationId)

      setRecommendation(result)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to evaluate automation",
      )
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium">
          Location
        </label>

        <select
          value={locationId}
          onChange={(event) => {
            setLocationId(event.target.value)
            setRecommendation(null)
            setMessage("")
          }}
          className="w-full rounded-lg border border-slate-300 p-2 text-sm"
        >
          {locations.length === 0 ? (
            <option value="">
              No locations available
            </option>
          ) : (
            locations.map((location) => (
              <option
                key={location.id}
                value={location.id}
              >
                {location.name}
              </option>
            ))
          )}
        </select>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">
          Strategy
        </label>

        <select
          value={strategyKey}
          onChange={(event) =>
            setStrategyKey(
              event.target.value as StrategyKey,
            )
          }
          className="w-full rounded-lg border border-slate-300 p-2 text-sm"
        >
          <option value="conservative">
            Conservative
          </option>

          <option value="aggressive">
            Aggressive
          </option>
        </select>
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={handleSave}
          disabled={loading || !locationId}
          className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Save Strategy
        </button>

        <button
          type="button"
          onClick={handleEvaluate}
          disabled={loading || !locationId}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium disabled:opacity-50"
        >
          Evaluate
        </button>
      </div>

      {message && (
        <p className="text-sm text-green-700">
          {message}
        </p>
      )}

      {error && (
        <p className="text-sm text-red-600">
          {error}
        </p>
      )}

      {recommendation && (
        <div className="rounded-lg bg-slate-50 p-3 text-sm">
          <p>
            <strong>Strategy:</strong>{" "}
            {recommendation.strategy_key}
          </p>

          <p>
            <strong>Action:</strong>{" "}
            {recommendation.action}
          </p>

          <p className="mt-1">
            <strong>Reason:</strong>{" "}
            {recommendation.reason}
          </p>
        </div>
      )}
    </div>
  )
}
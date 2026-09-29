import type { DeviceFamily } from "../../services/api"


type Props = {
  family: DeviceFamily
  onChange: (family: DeviceFamily) => void
}


export default function DeviceFamilySwitcher({
  family,
  onChange,
}: Props) {
  return (
    <div className="flex gap-2">
      <button
        type="button"
        onClick={() => onChange("simulation")}
        className={`rounded px-4 py-2 ${
          family === "simulation"
            ? "bg-slate-900 text-white"
            : "bg-slate-200 text-slate-900"
        }`}
      >
        Simulation
      </button>

      <button
        type="button"
        onClick={() => onChange("edge")}
        className={`rounded px-4 py-2 ${
          family === "edge"
            ? "bg-slate-900 text-white"
            : "bg-slate-200 text-slate-900"
        }`}
      >
        Edge
      </button>
    </div>
  )
}


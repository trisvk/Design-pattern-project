import { useState } from "react"

import SensorList from "../features/sensors/SensorList"
import DeviceList from "../components/devices/DeviceList"
import LocationConfigWizard from "../components/config/LocationConfigWizard"
import StrategyPanel from "../components/automation/StrategyPanel"
import OverviewPanel from "../components/overview/OverviewPanel"

const sections = [
  { id: "sensors", title: "Sensors" },
  { id: "devices", title: "Devices" },
  { id: "configuration", title: "Configuration" },
  { id: "automation", title: "Automation" },
  { id: "overview", title: "Overview" },
  { id: "controls", title: "Controls" },
  { id: "events", title: "Events" },
] as const

type SectionId = (typeof sections)[number]["id"]

export default function DashboardPage() {
  const [activeSection, setActiveSection] =
    useState<SectionId>("overview")

  function renderSection() {
    switch (activeSection) {
      case "sensors":
        return <SensorList />

      case "devices":
        return <DeviceList />

      case "configuration":
        return <LocationConfigWizard />

      case "automation":
        return <StrategyPanel />

      case "overview":
        return <OverviewPanel />

      default:
        return (
          <p className="text-sm text-slate-500">
            Placeholder for future phase.
          </p>
        )
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">
        Dashboard
      </h2>

      <nav className="flex gap-2 overflow-x-auto border-b border-slate-200 pb-3">
        {sections.map((section) => (
          <button
            key={section.id}
            type="button"
            onClick={() => setActiveSection(section.id)}
            className={`shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition ${
              activeSection === section.id
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-600 hover:bg-slate-100"
            }`}
          >
            {section.title}
          </button>
        ))}
      </nav>

      <section
        id={activeSection}
        className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
      >
        <h3 className="mb-4 text-lg font-semibold">
          {sections.find(
            (section) => section.id === activeSection
          )?.title}
        </h3>

        {renderSection()}
      </section>
    </div>
  )
}


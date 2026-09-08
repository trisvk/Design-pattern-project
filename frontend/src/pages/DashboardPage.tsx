const sections = [
  { id: "sensors", title: "Sensors" },
  { id: "config", title: "Config" },
  { id: "automation", title: "Automation" },
  { id: "overview", title: "Overview" },
  { id: "controls", title: "Controls" },
  { id: "events", title: "Events" },
]

export default function DashboardPage() {
  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">Dashboard</h2>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {sections.map((section) => (
          <section
            key={section.id}
            id={section.id}
            className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
          >
            <h3 className="font-semibold">{section.title}</h3>
            <p className="mt-2 text-sm text-slate-500">
              Placeholder for future phase.
            </p>
          </section>
        ))}
      </div>
    </div>
  )
}
import { Link, Outlet } from "react-router-dom"
import HealthStatus from "./HealthStatus"

export default function AppLayout() {
  return (
    <div className="min-h-screen">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-bold text-emerald-600">
              Smart Greenhouse
            </h1>

            <nav className="mt-2 flex gap-4">
              <Link to="/">Home</Link>
              <Link to="/dashboard">Dashboard</Link>
            </nav>
          </div>

          <HealthStatus />
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
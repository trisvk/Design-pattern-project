import { BrowserRouter, Route, Routes } from "react-router-dom"

import AppLayout from "./components/AppLayout"
import DashboardPage from "./pages/DashboardPage"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
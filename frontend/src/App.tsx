import { Suspense } from "react";
import { Routes, Route } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";
import LoadingSpinner from "./components/common/LoadingSpinner";
import {
  Landing,
  Login,
  Dashboard,
  ConsultationPage,
  PatientDetails,
  Analytics,
  Settings,
  Reminders,
  NotFound,
} from "./routes";
import ProtectedRoute from "./components/common/ProtectedRoute";


export default function App() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center bg-[hsl(var(--background))]">
          <LoadingSpinner />
        </div>
      }
    >
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />

        {/* Protected routes inside layout */}
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/consultation" element={<ConsultationPage />} />
          <Route path="/consultation/:id" element={<ConsultationPage />} />
          <Route path="/patient/:id" element={<PatientDetails />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/reminders" element={<Reminders />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
}

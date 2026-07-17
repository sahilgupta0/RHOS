import { lazy } from "react";


// Lazy loaded page components
const Landing = lazy(() => import("../pages/Landing"));
const Login = lazy(() => import("../pages/Login"));
const Dashboard = lazy(() => import("../pages/Dashboard"));
const ConsultationPage = lazy(() => import("../pages/Consultation"));
const PatientDetails = lazy(() => import("../pages/PatientDetails"));
const Analytics = lazy(() => import("../pages/Analytics"));
const Settings = lazy(() => import("../pages/Settings"));
const Reminders = lazy(() => import("../pages/Reminders"));
const NotFound = lazy(() => import("../pages/NotFound"));

export { Landing, Login, Dashboard, ConsultationPage, PatientDetails, Analytics, Settings, Reminders, NotFound };

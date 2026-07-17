import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../../context/AuthContext";
import {
  Stethoscope,
  Shield,
  Brain,
  Activity,
  MapPin,
  ArrowRight,
  Heart,
  Mic,
  Eye,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Triage",
    description: "Automatic priority classification using multi-agent pipeline to help identify urgent cases faster.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: Shield,
    title: "Medication Safety",
    description: "Drug interaction checks, allergy warnings, and generic alternative suggestions.",
    color: "from-emerald-500 to-teal-500",
  },
  {
    icon: Activity,
    title: "Clinical Summaries",
    description: "Auto-generated doctor notes and follow-up plans reviewed by treating physicians.",
    color: "from-violet-500 to-purple-500",
  },
  {
    icon: Mic,
    title: "Voice Input",
    description: "Hands-free consultation input using browser-native speech recognition.",
    color: "from-amber-500 to-orange-500",
  },
  {
    icon: Eye,
    title: "Image Analysis",
    description: "Upload medical images for AI-assisted visual description of findings.",
    color: "from-rose-500 to-pink-500",
  },
  {
    icon: MapPin,
    title: "Rural Coverage",
    description: "Designed for PHCs, ASHA workers, and rural healthcare coordination.",
    color: "from-indigo-500 to-blue-500",
  },
];

export default function Landing() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-[hsl(var(--background))]">
      {/* Navbar */}
      <nav className="fixed top-0 z-50 w-full border-b border-[hsl(var(--border))/0.5] glass">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-primary text-white shadow-lg">
              <Stethoscope className="h-6 w-6" />
            </div>
            <span className="text-xl font-bold text-gradient">RHOS</span>
          </div>
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="rounded-xl bg-gradient-primary px-5 py-2.5 text-sm font-medium text-white shadow-lg shadow-blue-500/25 transition-all hover:shadow-xl hover:shadow-blue-500/30"
              >
                Go to Dashboard
              </Link>
            ) : (
              <Link
                to="/login"
                className="rounded-xl bg-gradient-primary px-5 py-2.5 text-sm font-medium text-white shadow-lg shadow-blue-500/25 transition-all hover:shadow-xl hover:shadow-blue-500/30"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative flex min-h-screen items-center overflow-hidden pt-16">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-slate-900 dark:via-slate-900 dark:to-blue-950" />
        <div className="absolute right-0 top-1/4 h-[500px] w-[500px] rounded-full bg-blue-400/10 blur-3xl" />
        <div className="absolute left-1/4 bottom-1/4 h-[400px] w-[400px] rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="relative mx-auto max-w-7xl px-4 py-20 lg:px-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-1.5 text-sm font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                <Heart className="h-4 w-4" />
                Clinical Decision Support System
              </div>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl"
            >
              <span className="text-gradient">Smarter Healthcare</span>
              <br />
              for Rural India
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mx-auto mt-6 max-w-2xl text-lg text-[hsl(var(--muted-foreground))] leading-relaxed"
            >
              AI-powered clinical decision support for primary health centers.
              Assists doctors with triage, medication safety, and care coordination — while doctors
              always make the final medical decisions.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Link
                to={isAuthenticated ? "/dashboard" : "/login"}
                className="group flex items-center gap-2 rounded-2xl bg-gradient-primary px-8 py-4 text-lg font-semibold text-white shadow-xl shadow-blue-500/25 transition-all hover:shadow-2xl hover:shadow-blue-500/30"
              >
                Get Started
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
            </motion.div>

            {/* Safety notice */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="mt-8 text-xs text-[hsl(var(--muted-foreground))]"
            >
              ⚠️ RHOS is a Clinical Decision Support System — NOT an AI doctor.
              All medical decisions are made by qualified healthcare professionals.
            </motion.p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative py-24">
        <div className="mx-auto max-w-7xl px-4 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold sm:text-4xl">
              Powered by <span className="text-gradient">8 AI Agents</span>
            </h2>
            <p className="mt-4 text-[hsl(var(--muted-foreground))] max-w-xl mx-auto">
              Orchestrated pipeline for comprehensive clinical decision support
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="group rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 transition-all hover:shadow-xl hover:-translate-y-1"
              >
                <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${feature.color} text-white shadow-lg`}>
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[hsl(var(--border))] py-8">
        <div className="mx-auto max-w-7xl px-4 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
            <Stethoscope className="h-4 w-4" />
            <span>RHOS — Rural Health Operating System</span>
          </div>
          <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
            Clinical Decision Support Tool • Not a substitute for medical advice
          </p>
        </div>
      </footer>
    </div>
  );
}

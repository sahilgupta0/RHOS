import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { Stethoscope, Mail, Lock, ArrowRight, AlertCircle, User as UserIcon, Phone } from "lucide-react";

export default function Login() {
  const { login, register, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<"staff" | "patient">("staff");
  const [isSignUp, setIsSignUp] = useState(false);

  // Form states
  const [email, setEmail] = useState("doctor@rhos.in");
  const [password, setPassword] = useState("doctor123");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Redirect if already logged in
  if (isAuthenticated) {
    if (user?.role === "patient") {
      navigate(`/patient/${user.patient_id || "P001"}`, { replace: true });
    } else {
      navigate("/dashboard", { replace: true });
    }
    return null;
  }

  const handleTabChange = (tab: "staff" | "patient") => {
    setActiveTab(tab);
    setIsSignUp(false);
    setError("");
    if (tab === "staff") {
      setEmail("doctor@rhos.in");
      setPassword("doctor123");
    } else {
      setEmail("patient@rhos.in");
      setPassword("patient123");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (activeTab === "patient" && isSignUp) {
        await register({
          email,
          password,
          name,
          role: "patient" as any,
          phone,
        });
      } else {
        await login({ email, password });
      }
      
      const savedUser = localStorage.getItem("rhos_user");
      const userObj = savedUser ? JSON.parse(savedUser) : null;
      if (userObj?.role === "patient") {
        navigate(`/patient/${userObj.patient_id || "P001"}`);
      } else {
        navigate("/dashboard");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-slate-900 dark:via-slate-900 dark:to-blue-950 p-4">
      {/* Background blurs */}
      <div className="absolute right-1/4 top-1/4 h-[400px] w-[400px] rounded-full bg-blue-400/10 blur-3xl" />
      <div className="absolute left-1/4 bottom-1/4 h-[300px] w-[300px] rounded-full bg-cyan-400/10 blur-3xl" />

      <div className="relative w-full max-w-md">
        {/* Glass card */}
        <div className="glass rounded-3xl p-8 shadow-xl">
          {/* Logo */}
          <div className="mb-6 text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-primary text-white shadow-xl shadow-blue-500/25">
              <Stethoscope className="h-8 w-8" />
            </div>
            <h1 className="text-2xl font-bold">Welcome to <span className="text-gradient">RHOS</span></h1>
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              Rural Health Operating System
            </p>
          </div>

          {/* Tabs */}
          <div className="mb-6 flex rounded-xl bg-[hsl(var(--muted))] p-1">
            <button
              onClick={() => handleTabChange("staff")}
              className={`flex-1 rounded-lg py-2 text-sm font-medium transition-all ${
                activeTab === "staff"
                  ? "bg-[hsl(var(--background))] text-[hsl(var(--foreground))] shadow"
                  : "text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
              }`}
            >
              Clinical Staff
            </button>
            <button
              onClick={() => handleTabChange("patient")}
              className={`flex-1 rounded-lg py-2 text-sm font-medium transition-all ${
                activeTab === "patient"
                  ? "bg-[hsl(var(--background))] text-[hsl(var(--foreground))] shadow"
                  : "text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
              }`}
            >
              Patient Portal
            </button>
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-4 flex items-center gap-2 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:bg-rose-900/20 dark:text-rose-400">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {activeTab === "patient" && isSignUp && (
              <>
                <div>
                  <label className="mb-1.5 block text-sm font-medium">Full Name</label>
                  <div className="flex items-center gap-2 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2.5 focus-within:ring-2 focus-within:ring-[hsl(var(--ring))]/50">
                    <UserIcon className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full bg-transparent text-sm outline-none"
                      placeholder="Enter your name"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium">Phone Number</label>
                  <div className="flex items-center gap-2 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2.5 focus-within:ring-2 focus-within:ring-[hsl(var(--ring))]/50">
                    <Phone className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full bg-transparent text-sm outline-none"
                      placeholder="+91-XXXXX-XXXXX"
                      required
                    />
                  </div>
                </div>
              </>
            )}

            <div>
              <label className="mb-1.5 block text-sm font-medium">Email</label>
              <div className="flex items-center gap-2 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2.5 focus-within:ring-2 focus-within:ring-[hsl(var(--ring))]/50">
                <Mail className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-transparent text-sm outline-none"
                  placeholder={activeTab === "staff" ? "doctor@rhos.in" : "patient@rhos.in"}
                  required
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium">Password</label>
              <div className="flex items-center gap-2 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2.5 focus-within:ring-2 focus-within:ring-[hsl(var(--ring))]/50">
                <Lock className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-transparent text-sm outline-none"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="group flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-primary py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:shadow-xl disabled:opacity-60"
            >
              {loading ? (
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <>
                  {activeTab === "patient" && isSignUp ? "Sign Up" : "Sign In"}
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </>
              )}
            </button>
          </form>

          {/* Toggle Patient Sign In / Sign Up */}
          {activeTab === "patient" && (
            <div className="mt-4 text-center">
              <button
                onClick={() => {
                  setIsSignUp(!isSignUp);
                  setError("");
                }}
                className="text-sm font-semibold text-[hsl(var(--primary))] hover:underline bg-transparent border-none cursor-pointer"
              >
                {isSignUp ? "Already have an account? Sign In" : "New Patient? Create an Account"}
              </button>
            </div>
          )}

          {/* Demo credentials */}
          {!isSignUp && (
            <div className="mt-6 rounded-xl bg-[hsl(var(--muted))] p-4">
              <p className="mb-2 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                Demo Credentials
              </p>
              <div className="space-y-1 text-xs text-[hsl(var(--muted-foreground))]">
                {activeTab === "staff" ? (
                  <>
                    <p><strong>Doctor:</strong> doctor@rhos.in / doctor123</p>
                    <p><strong>Nurse:</strong> nurse@rhos.in / nurse123</p>
                    <p><strong>Admin:</strong> admin@rhos.in / admin123</p>
                  </>
                ) : (
                  <p><strong>Patient:</strong> patient@rhos.in / patient123</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Back link */}
        <div className="mt-4 text-center">
          <Link to="/" className="text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}

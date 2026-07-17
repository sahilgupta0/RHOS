import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";
import { getInitials } from "../../lib/utils";
import {
  Bell,
  Search,
  Moon,
  Sun,
  Menu,
  LogOut,
  User,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

interface TopbarProps {
  onMenuToggle: () => void;
}

export default function Topbar({ onMenuToggle }: TopbarProps) {
  const { user, logout } = useAuth();
  const { resolvedTheme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 lg:px-6">
      {/* Left — Mobile menu + Search */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className="rounded-lg p-2 hover:bg-[hsl(var(--accent))] lg:hidden transition-colors"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2 rounded-xl bg-[hsl(var(--muted))] px-3 py-2 w-72">
          <Search className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
          <input
            type="text"
            placeholder="Search patients, records..."
            className="w-full bg-transparent text-sm outline-none placeholder:text-[hsl(var(--muted-foreground))]"
          />
        </div>
      </div>

      {/* Right — Actions */}
      <div className="flex items-center gap-2">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 hover:bg-[hsl(var(--accent))] transition-colors"
          title={`Switch to ${resolvedTheme === "dark" ? "light" : "dark"} mode`}
        >
          {resolvedTheme === "dark" ? (
            <Sun className="h-5 w-5 text-amber-400" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </button>

        {/* Notifications */}
        <button className="relative rounded-lg p-2 hover:bg-[hsl(var(--accent))] transition-colors">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-rose-500" />
        </button>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-[hsl(var(--accent))] transition-colors"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-primary text-xs font-bold text-white">
              {user ? getInitials(user.name) : "U"}
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium">{user?.name || "User"}</p>
              <p className="text-[10px] text-[hsl(var(--muted-foreground))] capitalize">{user?.role || "doctor"}</p>
            </div>
          </button>

          {showUserMenu && (
            <div className="absolute right-0 top-12 z-50 w-48 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-lg animate-in">
              <div className="p-2">
                <button
                  onClick={() => { navigate("/settings"); setShowUserMenu(false); }}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-[hsl(var(--accent))] transition-colors"
                >
                  <User className="h-4 w-4" /> Profile Settings
                </button>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-colors"
                >
                  <LogOut className="h-4 w-4" /> Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

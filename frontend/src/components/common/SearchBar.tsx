import { useState, useEffect } from "react";
import { Search, X } from "lucide-react";
import { useDebounce } from "../../hooks/useDebounce";
import { cn } from "../../lib/utils";

interface SearchBarProps {
  onSearch: (value: string) => void;
  placeholder?: string;
  delay?: number;
  className?: string;
}

export default function SearchBar({
  onSearch,
  placeholder = "Search...",
  delay = 400,
  className,
}: SearchBarProps) {
  const [value, setValue] = useState("");
  const debouncedValue = useDebounce(value, delay);

  useEffect(() => {
    onSearch(debouncedValue);
  }, [debouncedValue, onSearch]);

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-xl bg-[hsl(var(--muted))] px-3 py-2 focus-within:ring-2 focus-within:ring-[hsl(var(--ring))]/50 transition-all",
        className
      )}
    >
      <Search className="h-4 w-4 text-[hsl(var(--muted-foreground))] shrink-0" />
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-transparent text-sm outline-none placeholder:text-[hsl(var(--muted-foreground))]"
      />
      {value && (
        <button
          onClick={() => setValue("")}
          className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}

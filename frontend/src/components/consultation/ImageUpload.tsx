import { useState } from "react";
import { UploadCloud, X, AlertCircle } from "lucide-react";

import { cn } from "../../lib/utils";

interface ImageUploadProps {
  onUpload: (file: File) => void;
  isLoading?: boolean;
  className?: string;
}

export default function ImageUpload({ onUpload, isLoading = false, className }: ImageUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setPreviewUrl(URL.createObjectURL(file));
      onUpload(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPreviewUrl(URL.createObjectURL(file));
      onUpload(file);
    }
  };

  const handleClear = () => {
    setPreviewUrl(null);
  };

  return (
    <div className={cn("w-full", className)}>
      {!previewUrl ? (
        <label
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className={cn(
            "flex flex-col items-center justify-center border-2 border-dashed rounded-2xl p-6 transition-all cursor-pointer text-center",
            dragActive
              ? "border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5"
              : "border-[hsl(var(--border))] hover:border-[hsl(var(--primary))]/50 hover:bg-[hsl(var(--muted))]/40"
          )}
        >
          <input
            type="file"
            onChange={handleFileChange}
            accept="image/*"
            className="hidden"
            disabled={isLoading}
          />
          <UploadCloud className="h-8 w-8 text-[hsl(var(--muted-foreground))] mb-2" />
          <p className="text-xs font-semibold">Click to upload clinical photo</p>
          <p className="text-[10px] text-[hsl(var(--muted-foreground))] mt-1">or drag and drop (PNG, JPG)</p>
        </label>
      ) : (
        <div className="relative rounded-2xl border border-[hsl(var(--border))] overflow-hidden bg-[hsl(var(--muted))] p-2">
          <img
            src={previewUrl}
            alt="Clinical Preview"
            className="w-full max-h-48 object-cover rounded-xl"
          />
          <button
            onClick={handleClear}
            disabled={isLoading}
            className="absolute top-4 right-4 bg-black/60 text-white rounded-full p-1.5 hover:bg-black/80 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
          <div className="flex items-center gap-1.5 p-2 text-[10px] text-[hsl(var(--muted-foreground))] leading-normal mt-1 border-t border-[hsl(var(--border))]/40">
            <AlertCircle className="h-3.5 w-3.5 text-amber-500 shrink-0" />
            <span>Images will be processed and described by AI. Medical evaluations require clinical verification.</span>
          </div>
        </div>
      )}
    </div>
  );
}

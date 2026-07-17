import { Component, type ErrorInfo, type ReactNode } from "react";

import { AlertOctagon } from "lucide-react";

interface Props {
  children?: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex min-h-[300px] flex-col items-center justify-center rounded-2xl border border-rose-200 bg-rose-50/50 p-6 text-center dark:border-rose-900/30 dark:bg-rose-950/10">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400">
            <AlertOctagon className="h-6 w-6" />
          </div>
          <h3 className="mt-4 text-base font-bold text-rose-800 dark:text-rose-400">Something went wrong</h3>
          <p className="mt-2 text-xs text-rose-600 dark:text-rose-400/70 max-w-sm">
            {this.state.error?.message || "An unexpected error occurred in this section of the app."}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 rounded-xl bg-rose-600 px-4 py-2 text-xs font-semibold text-white transition-colors hover:bg-rose-700"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

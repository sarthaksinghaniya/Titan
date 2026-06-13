"use client";

import React, { ReactNode } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface ApiErrorBoundaryProps {
  children: ReactNode;
  onError?: (error: Error) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary for API and runtime errors
 * Gracefully handles errors and provides user-friendly messages
 */
export class ApiErrorBoundary extends React.Component<ApiErrorBoundaryProps, State> {
  constructor(props: ApiErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error details for debugging
    console.error("[ErrorBoundary] Caught error:", {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });

    // Call optional error handler
    this.props.onError?.(error);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      const isNetworkError = 
        this.state.error.message.includes("Network error") ||
        this.state.error.message.includes("timeout") ||
        this.state.error.message.includes("backend server");

      const isValidationError = this.state.error.message.includes("Validation");

      return (
        <div className="flex items-center justify-center min-h-screen bg-titan-bg text-titan-text-primary p-4 relative overflow-hidden">
          {/* Background Effects */}
          <div className="fixed inset-0 pointer-events-none z-0">
            <div className="bg-grid absolute inset-0 opacity-40"></div>
            <div className="orb-1 top-[-200px] left-[-200px]"></div>
            <div className="orb-2 bottom-[-100px] right-[-100px] opacity-50"></div>
          </div>

          <div className="relative z-10 w-full max-w-md mx-auto">
            {/* Error Card */}
            <div className="titan-card p-1 glass relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-amber-500/10 pointer-events-none"></div>
              <div className="relative bg-titan-surface/90 rounded-[14px] p-6 z-10 border border-red-500/20 shadow-2xl">
                {/* Icon & Title */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="size-10 rounded-lg bg-red-500/10 flex items-center justify-center border border-red-500/20 shrink-0">
                    <AlertCircle className="w-5 h-5 text-red-400" />
                  </div>
                  <div>
                    <h1 className="text-base font-bold text-white tracking-wide">
                      {isNetworkError ? "Connection Failure" : 
                       isValidationError ? "Validation Mismatch" : 
                       "Execution Error"}
                    </h1>
                    <p className="text-[10px] text-white/30 tracking-widest uppercase font-mono">System Core Alert</p>
                  </div>
                </div>

                {/* Error Message */}
                <div className="mb-6">
                  <p className="text-titan-text-secondary text-sm leading-relaxed">
                    {this.state.error.message}
                  </p>

                  {isNetworkError && (
                    <div className="mt-4 p-4 bg-red-500/5 border border-red-500/10 rounded-xl text-xs text-titan-text-secondary space-y-2">
                      <strong className="text-red-400 block font-semibold">Troubleshooting Steps:</strong>
                      <ul className="space-y-1.5 ml-4 list-disc text-white/60">
                        <li>Verify the backend server is running on port 8000</li>
                        <li>Ensure Docker container networks are bridged</li>
                        <li>Check if the environment variables match your host</li>
                        <li>Refresh the connection or check local network</li>
                      </ul>
                    </div>
                  )}

                  {isValidationError && (
                    <div className="mt-4 p-4 bg-amber-500/5 border border-amber-500/10 rounded-xl text-xs text-amber-300">
                      The payload did not match the expected API structure. Please review parameters and retry.
                    </div>
                  )}
                </div>

                {/* Error Details (Development Only) */}
                {process.env.NODE_ENV === "development" && (
                  <div className="mb-6 p-4 bg-black/60 border border-white/5 rounded-xl text-[10px] font-mono text-white/40 overflow-auto max-h-32">
                    <p className="font-semibold text-white/60 mb-2 font-sans">Debug Traceback:</p>
                    <pre className="whitespace-pre-wrap break-words font-mono">
                      {this.state.error.stack}
                    </pre>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <Button
                    onClick={this.handleReset}
                    variant="primary"
                    className="flex items-center justify-center gap-2 flex-1 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 border border-red-500/20"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Retry Link
                  </Button>
                  <Button
                    onClick={() => window.location.href = "/"}
                    variant="ghost"
                    className="flex-1 text-white hover:bg-white/5 border border-white/5"
                  >
                    Abort to Core
                  </Button>
                </div>
              </div>
            </div>

            {/* Footer Help Text */}
            <p className="text-center text-xs text-white/20 mt-4 font-mono uppercase tracking-wider">
              Need assistance? Check the{" "}
              <a href="/docs" className="text-red-400 hover:text-red-300 underline underline-offset-2 transition-colors">
                API Docs
              </a>
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Hook for handling API errors in functional components
 */
export function useApiError() {
  const [error, setError] = React.useState<Error | null>(null);

  const handleError = (err: unknown) => {
    if (err instanceof Error) {
      setError(err);
      console.error("[useApiError] Error caught:", err.message);
    } else {
      const error = new Error(String(err));
      setError(error);
      console.error("[useApiError] Unknown error:", err);
    }
  };

  const clearError = () => setError(null);

  return { error, handleError, clearError };
}

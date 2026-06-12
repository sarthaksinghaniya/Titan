"use client";

import React from "react";
import { cn } from "@/lib/utils";

// ─── Skeleton ─────────────────────────────────────────────────
export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-shimmer rounded-lg bg-white/5", className)}
      {...props}
    />
  );
}

// ─── Spinner ──────────────────────────────────────────────────
interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function Spinner({ size = "md", className }: SpinnerProps) {
  const sizes = { sm: "size-4", md: "size-6", lg: "size-8" };
  return (
    <div
      className={cn(
        sizes[size],
        "border-2 border-white/10 border-t-indigo-500 rounded-full animate-spin",
        className
      )}
    />
  );
}

// ─── Progress Bar ─────────────────────────────────────────────
interface ProgressProps {
  value: number; // 0–100
  color?: string;
  label?: string;
  showValue?: boolean;
  className?: string;
}

export function Progress({ value, color = "#6366f1", label, showValue = false, className }: ProgressProps) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      {(label || showValue) && (
        <div className="flex items-center justify-between text-xs text-white/50">
          {label && <span>{label}</span>}
          {showValue && <span>{Math.round(value)}%</span>}
        </div>
      )}
      <div className="h-1.5 w-full rounded-full bg-white/5 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${Math.min(100, Math.max(0, value))}%`, background: color }}
        />
      </div>
    </div>
  );
}

// ─── Divider ──────────────────────────────────────────────────
interface DividerProps {
  label?: string;
  className?: string;
}

export function Divider({ label, className }: DividerProps) {
  if (label) {
    return (
      <div className={cn("flex items-center gap-3", className)}>
        <div className="flex-1 h-px bg-white/5" />
        <span className="text-xs text-white/30 font-medium">{label}</span>
        <div className="flex-1 h-px bg-white/5" />
      </div>
    );
  }
  return <div className={cn("h-px bg-white/5", className)} />;
}

// ─── Empty State ──────────────────────────────────────────────
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-4 py-16 text-center", className)}>
      {icon && (
        <div className="size-12 rounded-2xl bg-white/5 border border-white/5 flex items-center justify-center text-white/20">
          {icon}
        </div>
      )}
      <div className="space-y-1">
        <p className="text-sm font-medium text-white/60">{title}</p>
        {description && <p className="text-xs text-white/30 max-w-xs">{description}</p>}
      </div>
      {action}
    </div>
  );
}

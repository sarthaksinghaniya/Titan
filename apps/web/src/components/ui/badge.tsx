"use client";

import React from "react";
import { cn } from "@/lib/utils";
import type { SessionStatus } from "@titan/shared-types";

// ─── Badge ────────────────────────────────────────────────────
interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info" | "minister";
  ministerRole?: string;
  dot?: boolean;
}

export function Badge({
  variant = "default",
  ministerRole,
  dot = false,
  className,
  children,
  ...props
}: BadgeProps) {
  const variants = {
    default: "bg-white/5 text-white/60 border-white/10",
    success: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    warning: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    danger: "bg-red-500/15 text-red-400 border-red-500/30",
    info: "bg-sky-500/15 text-sky-400 border-sky-500/30",
    minister: ministerRole ? `badge-${ministerRole}` : "bg-white/5 text-white/60 border-white/10",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-medium rounded-full border",
        variants[variant],
        className
      )}
      {...props}
    >
      {dot && (
        <span className="size-1.5 rounded-full bg-current animate-pulse" />
      )}
      {children}
    </span>
  );
}

// ─── Status Badge ─────────────────────────────────────────────
const STATUS_CONFIG: Record<SessionStatus, { label: string; variant: BadgeProps["variant"]; pulse: boolean }> = {
  pending: { label: "Pending", variant: "default", pulse: false },
  analyzing: { label: "Analyzing", variant: "info", pulse: true },
  debating: { label: "Debating", variant: "warning", pulse: true },
  voting: { label: "Voting", variant: "minister", pulse: true },
  simulating: { label: "Simulating", variant: "info", pulse: true },
  synthesizing: { label: "Synthesizing", variant: "warning", pulse: true },
  completed: { label: "Completed", variant: "success", pulse: false },
  failed: { label: "Failed", variant: "danger", pulse: false },
};

interface StatusBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: SessionStatus;
}

export function StatusBadge({ status, className, ...props }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  return (
    <Badge
      variant={config.variant}
      dot={config.pulse}
      className={className}
      {...props}
    >
      {config.label}
    </Badge>
  );
}

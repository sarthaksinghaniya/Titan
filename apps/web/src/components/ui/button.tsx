"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "outline";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  isLoading = false,
  leftIcon,
  rightIcon,
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed select-none";

  const variants = {
    primary:
      "bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30",
    secondary:
      "bg-white/5 hover:bg-white/10 active:bg-white/5 text-white/80 hover:text-white border border-white/10 hover:border-white/20",
    ghost: "hover:bg-white/5 active:bg-white/5 text-white/60 hover:text-white/90",
    danger:
      "bg-red-600/20 hover:bg-red-600/30 active:bg-red-600/20 text-red-400 hover:text-red-300 border border-red-500/30",
    outline:
      "border border-white/10 hover:border-white/20 text-white/70 hover:text-white bg-transparent hover:bg-white/5",
  };

  const sizes = {
    sm: "text-xs px-3 py-1.5 h-7",
    md: "text-sm px-4 py-2 h-9",
    lg: "text-base px-6 py-3 h-11",
  };

  return (
    <button
      className={cn(base, variants[variant], sizes[size], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="size-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        leftIcon
      )}
      {children}
      {!isLoading && rightIcon}
    </button>
  );
}

"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftAdornment?: React.ReactNode;
}

export function Input({ label, error, leftAdornment, className, id, ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-white/70">
          {label}
        </label>
      )}
      <div className="relative">
        {leftAdornment && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40">
            {leftAdornment}
          </div>
        )}
        <input
          id={id}
          className={cn(
            "w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white/90",
            "placeholder:text-white/30 transition-all duration-200",
            "focus:outline-none focus:border-indigo-500/60 focus:bg-white/[0.07] focus:ring-1 focus:ring-indigo-500/30",
            "hover:border-white/15 hover:bg-white/[0.07]",
            leftAdornment && "pl-10",
            error && "border-red-500/50 focus:border-red-500/60 focus:ring-red-500/30",
            className
          )}
          {...props}
        />
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

// ─── Textarea ─────────────────────────────────────────────────
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export function Textarea({ label, error, hint, className, id, ...props }: TextareaProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <div className="flex items-center justify-between">
          <label htmlFor={id} className="text-sm font-medium text-white/70">
            {label}
          </label>
          {hint && <span className="text-xs text-white/35">{hint}</span>}
        </div>
      )}
      <textarea
        id={id}
        className={cn(
          "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white/90",
          "placeholder:text-white/30 transition-all duration-200 resize-none",
          "focus:outline-none focus:border-indigo-500/60 focus:bg-white/[0.07] focus:ring-1 focus:ring-indigo-500/30",
          "hover:border-white/15 hover:bg-white/[0.07]",
          error && "border-red-500/50",
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

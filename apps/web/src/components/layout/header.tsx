"use client";

import React from "react";
import { Bell, Settings, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export function Header({ title, subtitle, actions }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-8 py-4 border-b border-white/5 bg-titan-bg/80 backdrop-blur-sm sticky top-0 z-40">
      <div>
        {title && <h2 className="text-sm font-semibold text-white/90">{title}</h2>}
        {subtitle && <p className="text-xs text-white/40 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-2">
        {actions}
        <Button
          variant="ghost"
          size="sm"
          id="header-api-status"
          className="gap-1.5 text-emerald-400/80 hover:text-emerald-300"
        >
          <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
          API Live
        </Button>
        <Button variant="ghost" size="sm" id="header-notifications" aria-label="Notifications">
          <Bell className="size-4 text-white/40" />
        </Button>
        <Button variant="ghost" size="sm" id="header-settings" aria-label="Settings">
          <Settings className="size-4 text-white/40" />
        </Button>
      </div>
    </header>
  );
}

// ─── Page Shell ───────────────────────────────────────────────
interface PageShellProps {
  title?: string;
  subtitle?: string;
  headerActions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function PageShell({ title, subtitle, headerActions, children, className }: PageShellProps) {
  return (
    <div className={`flex flex-col flex-1 min-h-screen ${className ?? ""}`}>
      {(title || headerActions) && (
        <Header title={title} subtitle={subtitle} actions={headerActions} />
      )}
      <main className="flex-1">{children}</main>
    </div>
  );
}

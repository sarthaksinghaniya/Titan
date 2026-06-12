"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Crown,
  LayoutDashboard,
  History,
  FlaskConical,
  ChevronRight,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", icon: LayoutDashboard, label: "New Session", id: "nav-new-session" },
  { href: "/sessions", icon: History, label: "Sessions", id: "nav-sessions" },
] as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex flex-col w-60 shrink-0 border-r border-white/5 bg-titan-surface h-screen sticky top-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-white/5">
        <div className="relative size-8 rounded-lg bg-gradient-to-br from-amber-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
          <Crown className="size-4 text-white" />
          <div className="absolute -top-0.5 -right-0.5 size-2 rounded-full bg-emerald-400 border border-titan-surface animate-pulse" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-wide text-white">TITAN</h1>
          <p className="text-[10px] text-white/35 font-medium tracking-widest uppercase">
            Gov Intelligence
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <p className="text-[10px] font-semibold tracking-widest text-white/25 uppercase px-2 mb-3">
          Platform
        </p>
        {NAV_ITEMS.map(({ href, icon: Icon, label, id }) => {
          const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              id={id}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 group",
                isActive
                  ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/20"
                  : "text-white/50 hover:text-white/80 hover:bg-white/5"
              )}
            >
              <Icon
                className={cn(
                  "size-4 shrink-0",
                  isActive ? "text-indigo-400" : "text-white/30 group-hover:text-white/60"
                )}
              />
              <span className="flex-1">{label}</span>
              {isActive && <ChevronRight className="size-3 text-indigo-400/60" />}
            </Link>
          );
        })}
      </nav>

      {/* Status Bar */}
      <div className="p-3 border-t border-white/5">
        <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg bg-white/[0.03] border border-white/5">
          <div className="flex items-center gap-1.5">
            <FlaskConical className="size-3.5 text-indigo-400" />
            <span className="text-xs text-white/50 font-medium">AI Cabinet</span>
          </div>
          <div className="ml-auto flex items-center gap-1">
            <Zap className="size-3 text-amber-400" />
            <span className="text-[10px] text-amber-400/80 font-medium">Online</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

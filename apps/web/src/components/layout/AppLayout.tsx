'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  Hexagon, 
  LayoutDashboard, 
  Users, 
  Activity, 
  FileText,
  ActivitySquare
} from 'lucide-react';
import { useSessionStore } from '@/store/useSessionStore';
import { useEventStream } from '@/hooks/useEventStream';
import { ApiErrorBoundary } from '@/components/error/ApiErrorBoundary';

const navItems = [
  { href: '/', label: 'Command Center', icon: LayoutDashboard },
  { href: '/parliament', label: 'Live Parliament', icon: Users },
  { href: '/simulation', label: 'Future Engine', icon: Activity },
  { href: '/report', label: 'Final Directive', icon: FileText },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { projectId, phase, connected } = useSessionStore();
  
  // Initialize SSE connection globally when a projectId exists
  useEventStream(projectId);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-titan-bg text-titan-text-primary">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="bg-grid absolute inset-0 opacity-40"></div>
        <div className="orb-1 top-[-200px] left-[-200px]"></div>
        <div className="orb-2 bottom-[-100px] right-[-100px] opacity-50"></div>
      </div>

      {/* Sidebar Navigation */}
      <aside className="w-64 z-10 glass border-r border-titan-border flex flex-col justify-between">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-12">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-lg titan-surface border border-titan-border titan-glow">
              <Hexagon className="text-titan-gold w-6 h-6 absolute" />
              <Hexagon className="text-titan-gold w-6 h-6 absolute animate-pulse-glow" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-widest text-white">TITAN</h1>
              <p className="text-[10px] uppercase tracking-widest text-titan-blue-light opacity-80">Intelligence Core</p>
            </div>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link key={item.href} href={item.href} className="block relative">
                  {isActive && (
                    <motion.div
                      layoutId="activeNavIndicator"
                      className="absolute inset-0 bg-titan-blue/10 border-l-2 border-titan-blue rounded-r-md"
                      initial={false}
                      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />
                  )}
                  <div className={`relative flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${isActive ? 'text-white' : 'text-titan-text-secondary hover:text-white hover:bg-white/5'}`}>
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </div>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Status Indicator */}
        <div className="p-6 border-t border-titan-border/50">
          <div className="flex items-center justify-between text-xs font-mono uppercase tracking-wider mb-2 text-titan-text-secondary">
            <span>System Status</span>
            {connected ? (
              <span className="flex items-center gap-2 text-green-400">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                Online
              </span>
            ) : (
              <span className="text-titan-text-muted">Standby</span>
            )}
          </div>
          <div className="titan-surface p-3 rounded-md border border-titan-border">
            <div className="flex items-center gap-2 text-sm text-white">
              <ActivitySquare className="w-4 h-4 text-titan-blue-light" />
              <span className="font-mono">Phase: <span className={`status-${phase} font-bold`}>{phase.toUpperCase()}</span></span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 relative z-10 overflow-y-auto overflow-x-hidden">
        <div className="max-w-6xl mx-auto px-8 py-10">
          <ApiErrorBoundary>
            <motion.div
              key={pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          </ApiErrorBoundary>
        </div>
      </main>
    </div>
  );
}

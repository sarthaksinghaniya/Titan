"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  History,
  Plus,
  ArrowRight,
  Crown,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/badge";
import { Skeleton, EmptyState } from "@/components/ui/helpers";
import { PageShell } from "@/components/layout/header";
import { sessionsApi } from "@/lib/api-client";
import { useSessionsListStore } from "@/store/session-store";
import { formatRelativeTime, truncate } from "@/lib/utils";
import type { Session } from "@titan/shared-types";

function SessionCard({ session }: { session: Session }) {
  const isActive = !["completed", "failed"].includes(session.status);

  return (
    <Link
      href={`/sessions/${session.id}`}
      id={`session-card-${session.id}`}
      className="group flex items-center gap-4 px-5 py-4 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] hover:border-white/10 transition-all duration-150"
    >
      {/* Status Icon */}
      <div className="shrink-0 size-9 rounded-lg bg-white/5 flex items-center justify-center">
        {session.status === "completed" ? (
          <CheckCircle2 className="size-4 text-emerald-400" />
        ) : session.status === "failed" ? (
          <XCircle className="size-4 text-red-400" />
        ) : (
          <Loader2 className="size-4 text-indigo-400 animate-spin" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-white/80 group-hover:text-white transition-colors leading-snug mb-1 line-clamp-2">
          {truncate(session.problem, 120)}
        </p>
        <div className="flex items-center gap-3">
          <StatusBadge status={session.status} />
          <div className="flex items-center gap-1 text-xs text-white/30">
            <Clock className="size-3" />
            {formatRelativeTime(session.created_at)}
          </div>
        </div>
      </div>

      {/* Arrow */}
      <ArrowRight className="size-4 text-white/20 group-hover:text-white/50 group-hover:translate-x-0.5 transition-all shrink-0" />
    </Link>
  );
}

export default function SessionsPage() {
  const router = useRouter();
  const { sessions, isLoading, error, setSessions, setLoading, setError } =
    useSessionsListStore();

  async function loadSessions() {
    setLoading(true);
    setError(null);
    try {
      const response = await sessionsApi.list();
      setSessions(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sessions");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeSessions = sessions.filter(
    (s) => !["completed", "failed"].includes(s.status)
  );
  const completedSessions = sessions.filter((s) => s.status === "completed");
  const failedSessions = sessions.filter((s) => s.status === "failed");

  return (
    <PageShell
      title="Sessions"
      subtitle="All governance intelligence sessions"
      headerActions={
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            id="refresh-sessions-btn"
            onClick={() => void loadSessions()}
            isLoading={isLoading}
            leftIcon={<RefreshCw className="size-3.5" />}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            id="new-session-btn"
            onClick={() => router.push("/")}
            leftIcon={<Plus className="size-4" />}
          >
            New Session
          </Button>
        </div>
      }
    >
      <div className="px-8 py-6 max-w-3xl mx-auto space-y-8">
        {error && (
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <XCircle className="size-4 text-red-400 shrink-0" />
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-20 rounded-xl" />
            ))}
          </div>
        ) : sessions.length === 0 ? (
          <EmptyState
            icon={<History className="size-6" />}
            title="No sessions yet"
            description="Submit a societal problem to convene the AI cabinet and start your first session."
            action={
              <Button
                variant="primary"
                size="sm"
                id="empty-new-session-btn"
                onClick={() => router.push("/")}
                leftIcon={<Plus className="size-4" />}
              >
                Start First Session
              </Button>
            }
          />
        ) : (
          <>
            {activeSessions.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <Loader2 className="size-3.5 text-indigo-400 animate-spin" />
                  <h2 className="text-xs font-semibold text-white/50 uppercase tracking-widest">
                    Active ({activeSessions.length})
                  </h2>
                </div>
                <div className="space-y-2">
                  {activeSessions.map((session) => (
                    <SessionCard key={session.id} session={session} />
                  ))}
                </div>
              </section>
            )}

            {completedSessions.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 className="size-3.5 text-emerald-400" />
                  <h2 className="text-xs font-semibold text-white/50 uppercase tracking-widest">
                    Completed ({completedSessions.length})
                  </h2>
                </div>
                <div className="space-y-2">
                  {completedSessions.map((session) => (
                    <SessionCard key={session.id} session={session} />
                  ))}
                </div>
              </section>
            )}

            {failedSessions.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <XCircle className="size-3.5 text-red-400" />
                  <h2 className="text-xs font-semibold text-white/50 uppercase tracking-widest">
                    Failed ({failedSessions.length})
                  </h2>
                </div>
                <div className="space-y-2">
                  {failedSessions.map((session) => (
                    <SessionCard key={session.id} session={session} />
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </PageShell>
  );
}

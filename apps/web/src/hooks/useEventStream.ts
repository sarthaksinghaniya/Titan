/**
 * useEventStream — React hook for consuming SSE from the TITAN API.
 *
 * Hardening changes (Step 7.1):
 * - Removed `phase` from the dependency array. Including it caused the
 *   effect to re-run (and re-subscribe) on every phase_changed event,
 *   creating a reconnect loop during active graph execution.
 * - Added a `isTerminal` ref so that once session_complete or error is
 *   received the EventSource is closed and never re-opened for the same
 *   projectId, even if the component re-renders.
 * - The effect now uses `projectIdRef` to avoid stale closure bugs when
 *   projectId changes while events are in-flight.
 * - Error handling: if readyState is CONNECTING (not CLOSED) after the
 *   onerror fires, we do NOT mark disconnected — EventSource will retry
 *   automatically.
 */
import { useEffect, useRef } from 'react';
import { useSessionStore } from '../store/useSessionStore';

export function useEventStream(projectId: string | null) {
  const {
    setPhase,
    setError,
    setConnected,
    appendAnalysis,
    appendDebate,
    appendVote,
    setSimulations,
    setFinalReport,
  } = useSessionStore();

  const eventSourceRef = useRef<EventSource | null>(null);
  // Tracks whether this projectId's stream has already terminated.
  const isTerminalRef = useRef<boolean>(false);
  // Tracks the projectId the current EventSource is open for.
  const projectIdRef = useRef<string | null>(null);

  useEffect(() => {
    // No project yet — nothing to subscribe to.
    if (!projectId) return;

    // If the projectId changed, reset the terminal flag.
    if (projectIdRef.current !== projectId) {
      isTerminalRef.current = false;
      projectIdRef.current = projectId;
    }

    // Once terminal (session_complete / error) never reconnect for the
    // same projectId, even if the component re-renders.
    if (isTerminalRef.current) return;

    // Close any pre-existing EventSource (e.g. from a previous projectId).
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    const isServer = typeof window === 'undefined';
    const apiUrl = isServer
      ? (process.env.INTERNAL_API_URL ??
         process.env.NEXT_PUBLIC_API_URL ??
         'http://localhost:8000')
      : ''; // Browser: use relative path through Next.js proxy
    const url = `${apiUrl}/api/v1/sessions/${projectId}/stream`;

    console.log(`[SSE] Connecting to: ${url}`);
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onopen = () => {
      console.log('[SSE] Connection opened');
      setConnected(true);
    };

    es.onerror = () => {
      // EventSource auto-reconnects when readyState is CONNECTING.
      // Only mark disconnected if the connection is definitively CLOSED.
      if (es.readyState === EventSource.CLOSED) {
        console.warn('[SSE] Connection closed');
        setConnected(false);
      } else {
        console.warn('[SSE] Connection error — EventSource will retry');
      }
    };

    es.onmessage = (event: MessageEvent<string>) => {
      try {
        const payload = JSON.parse(event.data) as {
          event: string;
          data: Record<string, unknown>;
        };
        const { event: eventName, data } = payload;

        switch (eventName) {
          case 'heartbeat':
            setConnected(true);
            break;

          case 'session_started':
            setPhase('analyzing');
            break;

          case 'phase_changed':
            setPhase(data.new_phase as Parameters<typeof setPhase>[0]);
            break;

          case 'minister_analysis': {
            const analysis = data.analysis as Record<string, unknown>;
            appendAnalysis(analysis);
            if (analysis.agent_role) {
              // Synthesize a presentation entry for the debate timeline.
              appendDebate({
                agent_role: analysis.agent_role,
                phase: 'presentation',
                round_number: 0,
                argument: `Situation Assessment: ${analysis.situation_assessment}\n\nProposed Solutions: ${
                  Array.isArray(analysis.proposed_solutions)
                    ? (analysis.proposed_solutions as string[]).join(', ')
                    : ''
                }`,
                _timestamp: new Date().toISOString(),
              });
            }
            break;
          }

          case 'debate_argument':
          case 'opposition_attack':
          case 'rebuttal':
            appendDebate(data.argument);
            break;

          case 'minister_vote':
            appendVote(data.vote);
            break;

          case 'simulation_complete':
            setSimulations(data.results as unknown[]);
            break;

          case 'session_complete':
            setFinalReport(data.final_report);
            // Mark terminal BEFORE closing so the cleanup effect below
            // does not see a non-terminal close and try to reconnect.
            isTerminalRef.current = true;
            es.close();
            setConnected(false);
            break;

          case 'error':
            setError((data.message as string) ?? 'Unknown error');
            isTerminalRef.current = true;
            es.close();
            setConnected(false);
            break;

          default:
            break;
        }
      } catch (err) {
        console.error('[SSE] Failed to parse message:', err);
      }
    };

    // Cleanup on unmount or projectId change.
    return () => {
      console.log('[SSE] Closing connection (cleanup)');
      es.close();
      eventSourceRef.current = null;
      setConnected(false);
    };
    // Intentionally excludes `phase` — including it caused a reconnect
    // loop on every phase_changed event.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    projectId,
    setPhase,
    setError,
    setConnected,
    appendAnalysis,
    appendDebate,
    appendVote,
    setSimulations,
    setFinalReport,
  ]);
}

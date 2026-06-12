import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type {
  Session,
  MinisterAnalysis,
  DebateRound,
  Vote,
  SimulationResult,
  FinalPolicy,
  SSEEvent,
  SessionStatus,
} from "@titan/shared-types";

// ─── Types ────────────────────────────────────────────────────
interface LiveSessionState {
  session: Session | null;
  analyses: MinisterAnalysis[];
  debateRounds: DebateRound[];
  votes: Vote[];
  simulationResults: SimulationResult[];
  finalPolicy: FinalPolicy | null;
  streamingTexts: Record<string, string>; // minister_role -> current chunk
  isConnected: boolean;
  currentPhase: SessionStatus;
}

interface SessionStore extends LiveSessionState {
  // Actions
  setSession: (session: Session) => void;
  updateSessionStatus: (status: SessionStatus) => void;
  addAnalysis: (analysis: MinisterAnalysis) => void;
  updateStreamingText: (ministerRole: string, chunk: string) => void;
  clearStreamingText: (ministerRole: string) => void;
  addDebateRound: (round: DebateRound) => void;
  addVote: (vote: Vote) => void;
  addSimulationResult: (result: SimulationResult) => void;
  setFinalPolicy: (policy: FinalPolicy) => void;
  setConnected: (connected: boolean) => void;
  setCurrentPhase: (phase: SessionStatus) => void;
  handleSSEEvent: (event: SSEEvent) => void;
  reset: () => void;
}

const initialState: LiveSessionState = {
  session: null,
  analyses: [],
  debateRounds: [],
  votes: [],
  simulationResults: [],
  finalPolicy: null,
  streamingTexts: {},
  isConnected: false,
  currentPhase: "pending",
};

export const useSessionStore = create<SessionStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setSession: (session) => set({ session }),

      updateSessionStatus: (status) =>
        set((state) => ({
          session: state.session ? { ...state.session, status } : null,
        })),

      addAnalysis: (analysis) =>
        set((state) => ({
          analyses: [...state.analyses.filter((a) => a.minister_role !== analysis.minister_role), analysis],
        })),

      updateStreamingText: (ministerRole, chunk) =>
        set((state) => ({
          streamingTexts: {
            ...state.streamingTexts,
            [ministerRole]: (state.streamingTexts[ministerRole] ?? "") + chunk,
          },
        })),

      clearStreamingText: (ministerRole) =>
        set((state) => {
          const updated = { ...state.streamingTexts };
          delete updated[ministerRole];
          return { streamingTexts: updated };
        }),

      addDebateRound: (round) =>
        set((state) => ({ debateRounds: [...state.debateRounds, round] })),

      addVote: (vote) =>
        set((state) => ({
          votes: [...state.votes.filter((v) => v.minister_role !== vote.minister_role), vote],
        })),

      addSimulationResult: (result) =>
        set((state) => ({ simulationResults: [...state.simulationResults, result] })),

      setFinalPolicy: (policy) => set({ finalPolicy: policy }),

      setConnected: (connected) => set({ isConnected: connected }),

      setCurrentPhase: (phase) => set({ currentPhase: phase }),

      handleSSEEvent: (event) => {
        const store = get();
        switch (event.event) {
          case "session_started":
            store.setConnected(true);
            store.setCurrentPhase("analyzing");
            break;
          case "analysis_started":
            store.setCurrentPhase("analyzing");
            break;
          case "analysis_complete": {
            const data = event.data as { analysis: MinisterAnalysis };
            if (data.analysis) store.addAnalysis(data.analysis);
            break;
          }
          case "debate_started":
            store.setCurrentPhase("debating");
            break;
          case "debate_argument": {
            const data = event.data as { chunk: string; minister_role: string; is_complete: boolean; debate_round?: DebateRound };
            if (data.chunk) store.updateStreamingText(data.minister_role, data.chunk);
            if (data.is_complete && data.debate_round) {
              store.addDebateRound(data.debate_round);
              store.clearStreamingText(data.minister_role);
            }
            break;
          }
          case "voting_started":
            store.setCurrentPhase("voting");
            break;
          case "vote_cast": {
            const data = event.data as { vote: Vote };
            if (data.vote) store.addVote(data.vote);
            break;
          }
          case "simulation_started":
            store.setCurrentPhase("simulating");
            break;
          case "simulation_result": {
            const data = event.data as { result: SimulationResult };
            if (data.result) store.addSimulationResult(data.result);
            break;
          }
          case "synthesis_started":
            store.setCurrentPhase("synthesizing");
            break;
          case "synthesis_complete": {
            const data = event.data as { policy: FinalPolicy };
            if (data.policy) store.setFinalPolicy(data.policy);
            break;
          }
          case "session_complete":
            store.setCurrentPhase("completed");
            store.setConnected(false);
            break;
          case "error":
            store.setCurrentPhase("failed");
            store.setConnected(false);
            break;
        }
      },

      reset: () => set(initialState),
    }),
    { name: "titan-session-store" }
  )
);

// ─── Sessions List Store ───────────────────────────────────────
interface SessionsListStore {
  sessions: Session[];
  isLoading: boolean;
  error: string | null;
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useSessionsListStore = create<SessionsListStore>()(
  devtools(
    (set) => ({
      sessions: [],
      isLoading: false,
      error: null,
      setSessions: (sessions) => set({ sessions }),
      addSession: (session) =>
        set((state) => ({ sessions: [session, ...state.sessions] })),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
    }),
    { name: "titan-sessions-list-store" }
  )
);

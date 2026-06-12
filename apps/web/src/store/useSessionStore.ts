import { create } from 'zustand';

export type SessionPhase = 'pending' | 'analyzing' | 'debating' | 'voting' | 'simulating' | 'synthesizing' | 'completed' | 'failed';

export interface StateData {
  projectId: string | null;
  phase: SessionPhase;
  error: string | null;
  analyses: any[];
  debates: any[];
  votes: any[];
  simulations: any[];
  finalReport: any | null;
  connected: boolean;
}

interface SessionStore extends StateData {
  setProjectId: (id: string) => void;
  setPhase: (phase: SessionPhase) => void;
  setError: (error: string) => void;
  setConnected: (status: boolean) => void;
  appendAnalysis: (analysis: any) => void;
  appendDebate: (debate: any) => void;
  appendVote: (vote: any) => void;
  setSimulations: (simulations: any[]) => void;
  setFinalReport: (report: any) => void;
  resetSession: () => void;
}

const initialState: StateData = {
  projectId: null,
  phase: 'pending',
  error: null,
  analyses: [],
  debates: [],
  votes: [],
  simulations: [],
  finalReport: null,
  connected: false,
};

export const useSessionStore = create<SessionStore>((set) => ({
  ...initialState,
  
  setProjectId: (id) => set({ projectId: id, error: null }),
  setPhase: (phase) => set({ phase }),
  setError: (error) => set({ error, phase: 'failed' }),
  setConnected: (status) => set({ connected: status }),
  
  appendAnalysis: (analysis) => set((state) => ({ 
    analyses: [...state.analyses.filter(a => a.agent_role !== analysis.agent_role), analysis] 
  })),
  
  appendDebate: (debate) => set((state) => ({ 
    debates: [...state.debates, debate] 
  })),
  
  appendVote: (vote) => set((state) => ({ 
    votes: [...state.votes.filter(v => v.agent_role !== vote.agent_role), vote] 
  })),
  
  setSimulations: (simulations) => set({ simulations }),
  setFinalReport: (report) => set({ finalReport: report, phase: 'completed' }),
  
  resetSession: () => set(initialState),
}));

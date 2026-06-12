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

  useEffect(() => {
    if (!projectId) return;

    const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/sessions/${projectId}/stream`;
    console.log(`Connecting to SSE: ${url}`);
    
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onopen = () => {
      console.log('SSE connection opened');
      setConnected(true);
    };

    es.onerror = (err) => {
      console.error('SSE connection error:', err);
      // Wait for a bit before showing error as EventSource auto-reconnects
      setTimeout(() => {
        if (es.readyState === EventSource.CLOSED) {
          setConnected(false);
        }
      }, 5000);
    };

    es.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const { event: eventName, data } = payload;
        
        switch (eventName) {
          case 'heartbeat':
            setConnected(true);
            break;
            
          case 'phase_changed':
            setPhase(data.new_phase);
            break;
            
          case 'minister_analysis':
            appendAnalysis(data.analysis);
            if (data.analysis.agent_role) {
                // Synthesize an initial presentation debate argument
                appendDebate({
                    agent_role: data.analysis.agent_role,
                    phase: 'presentation',
                    round_number: 0,
                    argument: `Situation Assessment: ${data.analysis.situation_assessment}\n\nProposed Solutions: ${data.analysis.proposed_solutions?.join(', ')}`,
                    _timestamp: new Date().toISOString()
                });
            }
            break;
            
          case 'debate_argument':
          case 'opposition_attack':
          case 'rebuttal':
            appendDebate(data.argument);
            break;
            
          case 'minister_vote':
            appendVote(data.vote);
            break;
            
          case 'simulation_complete':
            setSimulations(data.results);
            break;
            
          case 'session_complete':
            setFinalReport(data.final_report);
            es.close();
            setConnected(false);
            break;
            
          case 'error':
            setError(data.message);
            es.close();
            setConnected(false);
            break;
        }
      } catch (err) {
        console.error('Failed to parse SSE message:', err);
      }
    };

    return () => {
      console.log('Closing SSE connection');
      es.close();
      eventSourceRef.current = null;
      setConnected(false);
    };
  }, [projectId, setPhase, setError, setConnected, appendAnalysis, appendDebate, appendVote, setSimulations, setFinalReport]);
}

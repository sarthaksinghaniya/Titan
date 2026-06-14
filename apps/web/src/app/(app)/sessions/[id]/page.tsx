'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useSessionStore } from '@/store/useSessionStore';
import { sessionsApi } from '@/lib/api-client';
import { Loader2, XCircle } from 'lucide-react';

export default function SessionDetailRouter() {
  const router = useRouter();
  const { id } = useParams() as { id: string };
  const { 
    setProjectId, 
    setProblemText, 
    setPhase, 
    setError,
    appendAnalysis,
    appendDebate,
    appendVote,
    setSimulations,
    setFinalReport,
    resetSession
  } = useSessionStore();
  const [loadingError, setLoadingError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    async function loadAndRouteSession() {
      try {
        resetSession();
        // 1. Get the session status and info
        const session = await sessionsApi.get(id);
        
        setProjectId(session.id);
        setProblemText(session.problem);
        setPhase(session.status as any);

        if (session.status === 'completed') {
          // 2. If completed, load full report details (cast to any for runtime field access)
          const reportData = (await sessionsApi.getReport(id)) as any;
          
          // Populate the store with all historical items
          if (reportData.agents) {
            reportData.agents.forEach((a: any) => {
              appendAnalysis({
                agent_role: a.role,
                role_title: a.role,
                situation_assessment: a.analysis,
                primary_goal: a.analysis,
                key_findings: a.key_points,
                proposed_solutions: a.proposed_solutions,
                red_lines: a.concerns,
                priority_score: 50.0,
                confidence: 50.0
              });
            });
          }
          if (reportData.debates) {
            reportData.debates.forEach((d: any) => {
              appendDebate({
                agent_role: d.supporting_agents?.[0] || 'citizen_minister',
                round_number: d.round_number,
                phase: d.phase,
                argument: d.argument,
                attacking_roles: d.opposing_agents,
                defending_positions: d.supporting_agents,
                word_count: d.word_count,
                _timestamp: d.created_at
              });
            });
          }
          if (reportData.votes) {
            reportData.votes.forEach((v: any) => {
              appendVote({
                agent_role: v.agent_id || 'citizen_minister',
                voted_option: v.voted_option,
                confidence_score: v.confidence_score,
                justification: v.justification
              });
            });
          }
          if (reportData.simulations) {
            const mappedSims = reportData.simulations.map((s: any) => ({
              future_name: s.future_name || s.option_description || s.option_name,
              option_name: s.option_name,
              economic_score: s.economic_score,
              infrastructure_score: s.infrastructure_score,
              technology_score: s.technology_score,
              environmental_score: s.environmental_score,
              social_score: s.social_score,
              composite_score: s.composite_score,
              risk_level: s.risk_level,
              key_risks: s.key_risks,
              key_benefits: s.key_benefits
            }));
            setSimulations(mappedSims);
          }
          if (reportData.final_report) {
            setFinalReport({
              executive_summary: reportData.final_report.executive_summary,
              chosen_option: reportData.final_report.chosen_option,
              rationale: reportData.final_report.overall_rationale,
              confidence_score: reportData.final_report.confidence_score,
              implementation_steps: reportData.final_report.implementation_steps,
              success_metrics: reportData.final_report.success_metrics,
              risks_and_mitigations: reportData.final_report.risks_and_mitigations,
              expected_outcomes: reportData.final_report.expected_outcomes,
              review_timeline: reportData.final_report.review_timeline,
              vote_breakdown: { total_votes: reportData.final_report.total_votes },
              consensus_level: reportData.final_report.consensus_level,
              black_swan_crisis: reportData.final_report.black_swan_crisis,
              black_swan_impact: reportData.final_report.black_swan_impact,
              resilience_score: reportData.final_report.resilience_score
            });
          }
          if (reportData.executive_reports) {
            setExecutiveReports(reportData.executive_reports);
          }
          
          router.push('/report');
        } else if (session.status === 'failed') {
          setError(session.error_message || 'Session failed');
          
          try {
            const reportData = (await sessionsApi.getReport(id)) as any;
            if (reportData.agents) {
              reportData.agents.forEach((a: any) => {
                appendAnalysis({
                  agent_role: a.role,
                  role_title: a.role,
                  situation_assessment: a.analysis,
                  primary_goal: a.analysis,
                  key_findings: a.key_points,
                  proposed_solutions: a.proposed_solutions,
                  red_lines: a.concerns,
                  priority_score: 50.0,
                  confidence: 50.0
                });
              });
            }
            if (reportData.debates) {
              reportData.debates.forEach((d: any) => {
                appendDebate({
                  agent_role: d.supporting_agents?.[0] || 'citizen_minister',
                  round_number: d.round_number,
                  phase: d.phase,
                  argument: d.argument,
                  attacking_roles: d.opposing_agents,
                  defending_positions: d.supporting_agents,
                  word_count: d.word_count,
                  _timestamp: d.created_at
                });
              });
            }
            if (reportData.votes) {
              reportData.votes.forEach((v: any) => {
                appendVote({
                  agent_role: v.agent_id || 'citizen_minister',
                  voted_option: v.voted_option,
                  confidence_score: v.confidence_score,
                  justification: v.justification
                });
              });
            }
          } catch (e) {
            console.error('Failed to load partial report data for failed session:', e);
          }
          
          router.push('/parliament');
        } else {
          // If active (analyzing, debating, voting, simulating, synthesizing)
          try {
            const reportData = (await sessionsApi.getReport(id)) as any;
            if (reportData.agents) {
              reportData.agents.forEach((a: any) => {
                appendAnalysis({
                  agent_role: a.role,
                  role_title: a.role,
                  situation_assessment: a.analysis,
                  primary_goal: a.analysis,
                  key_findings: a.key_points,
                  proposed_solutions: a.proposed_solutions,
                  red_lines: a.concerns,
                  priority_score: 50.0,
                  confidence: 50.0
                });
              });
            }
            if (reportData.debates) {
              reportData.debates.forEach((d: any) => {
                appendDebate({
                  agent_role: d.supporting_agents?.[0] || 'citizen_minister',
                  round_number: d.round_number,
                  phase: d.phase,
                  argument: d.argument,
                  attacking_roles: d.opposing_agents,
                  defending_positions: d.supporting_agents,
                  word_count: d.word_count,
                  _timestamp: d.created_at
                });
              });
            }
            if (reportData.votes) {
              reportData.votes.forEach((v: any) => {
                appendVote({
                  agent_role: v.agent_id || 'citizen_minister',
                  voted_option: v.voted_option,
                  confidence_score: v.confidence_score,
                  justification: v.justification
                });
              });
            }
            if (reportData.simulations) {
              const mappedSims = reportData.simulations.map((s: any) => ({
                future_name: s.future_name || s.option_description || s.option_name,
                option_name: s.option_name,
                economic_score: s.economic_score,
                infrastructure_score: s.infrastructure_score,
                technology_score: s.technology_score,
                environmental_score: s.environmental_score,
                social_score: s.social_score,
                composite_score: s.composite_score,
                risk_level: s.risk_level,
                key_risks: s.key_risks,
                key_benefits: s.key_benefits
              }));
              setSimulations(mappedSims);
            }
          } catch (e) {
            // Ignore if relations are not populated
          }

          if (session.status === 'simulating') {
            router.push('/simulation');
          } else {
            router.push('/parliament');
          }
        }
      } catch (err: any) {
        console.error('Failed to load session:', err);
        setLoadingError(err.message || 'Failed to load session details');
      }
    }

    void loadAndRouteSession();
  }, [id, router, setProjectId, setProblemText, setPhase, setError, appendAnalysis, appendDebate, appendVote, setSimulations, setFinalReport, resetSession]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-white space-y-4">
      {loadingError ? (
        <div className="flex flex-col items-center max-w-md text-center p-6 rounded-xl bg-red-500/10 border border-red-500/20 space-y-3">
          <XCircle className="size-10 text-red-400" />
          <h2 className="text-lg font-bold">Error Loading Session</h2>
          <p className="text-sm text-red-300">{loadingError}</p>
          <button 
            onClick={() => router.push('/sessions')}
            className="px-4 py-2 mt-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-semibold transition"
          >
            Back to Sessions
          </button>
        </div>
      ) : (
        <>
          <Loader2 className="size-8 text-titan-blue animate-spin" />
          <p className="text-white/60 text-sm animate-pulse">Synchronizing cabinet intelligence...</p>
        </>
      )}
    </div>
  );
}

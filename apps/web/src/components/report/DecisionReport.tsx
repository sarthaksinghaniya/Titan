'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useSessionStore } from '@/store/useSessionStore';
import { FileText, CheckCircle, ShieldAlert, Zap, Layers } from 'lucide-react';

export function DecisionReport() {
  const { finalReport, phase } = useSessionStore();

  if (!finalReport && phase !== 'completed') return null;
  if (!finalReport) {
    return (
      <div className="titan-card p-12 flex flex-col items-center justify-center h-[500px]">
        <Layers className="w-12 h-12 text-titan-gold animate-spin-slow mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">Synthesizing Final Directive</h3>
        <p className="text-titan-text-secondary">Prime Minister is drafting the binding policy...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="titan-card p-8 border-t-4 border-t-titan-gold relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <FileText className="w-48 h-48" />
        </div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <span className="bg-titan-gold/20 text-titan-gold px-3 py-1 rounded text-xs font-bold tracking-widest uppercase">
              Binding Policy Directive
            </span>
            <span className="text-titan-text-muted text-sm font-mono">
              Consensus: <span className="text-white uppercase">{finalReport.consensus_level}</span>
            </span>
          </div>
          
          <h2 className="text-3xl font-black text-white mb-4">
            {finalReport.chosen_option}
          </h2>
          
          <p className="text-lg text-titan-text-secondary max-w-4xl leading-relaxed">
            {finalReport.executive_summary}
          </p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Col: Rationale & Steps */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="titan-surface-2 p-6 rounded-xl border border-titan-border"
          >
            <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-titan-blue-light" />
              Strategic Rationale
            </h3>
            <p className="text-titan-text-secondary leading-relaxed">
              {finalReport.overall_rationale}
            </p>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="titan-surface-2 p-6 rounded-xl border border-titan-border"
          >
            <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-6">
              <Layers className="w-5 h-5 text-titan-blue-light" />
              Implementation Roadmap
            </h3>
            <div className="space-y-6">
              {finalReport.implementation_steps?.map((step: any, idx: number) => (
                <div key={idx} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-titan-blue/20 text-titan-blue border border-titan-blue/50 flex items-center justify-center font-bold text-sm">
                      {idx + 1}
                    </div>
                    {idx !== finalReport.implementation_steps.length - 1 && (
                      <div className="w-px h-full bg-titan-border mt-2"></div>
                    )}
                  </div>
                  <div className="pb-6">
                    <h4 className="text-white font-bold text-lg mb-1">{step.phase}</h4>
                    <div className="flex items-center gap-3 text-xs text-titan-text-muted font-mono mb-3 uppercase">
                      <span>{step.duration}</span>
                      <span>•</span>
                      <span className="text-titan-gold">{step.budget_allocation_percent}% Budget</span>
                      <span>•</span>
                      <span className="text-titan-blue-light">{step.responsible_ministry}</span>
                    </div>
                    <ul className="space-y-2">
                      {step.actions?.map((action: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-titan-text-secondary">
                          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 shrink-0" />
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right Col: Metrics & Risks */}
        <div className="space-y-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="titan-card p-6 border-t-2 border-t-green-500"
          >
            <h3 className="text-lg font-bold text-white mb-4">Confidence Score</h3>
            <div className="flex items-end gap-2 mb-6">
              <span className="text-5xl font-black text-green-400 leading-none">
                {finalReport.confidence_score?.toFixed(1) || '85.0'}
              </span>
              <span className="text-titan-text-muted mb-1">/ 100</span>
            </div>
            
            <div className="w-full bg-black/40 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: `${finalReport.confidence_score || 85}%` }}
              ></div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="titan-surface p-6 rounded-xl border border-titan-border"
          >
            <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
              <CheckCircle className="w-5 h-5 text-green-400" />
              Success Metrics
            </h3>
            <ul className="space-y-4">
              {finalReport.success_metrics?.map((metric: any, idx: number) => (
                <li key={idx} className="text-sm">
                  <div className="text-white font-medium mb-1">{metric.metric}</div>
                  <div className="text-titan-text-secondary flex items-center justify-between">
                    <span className="text-green-400">{metric.target}</span>
                    <span className="text-xs font-mono text-titan-text-muted uppercase">{metric.deadline}</span>
                  </div>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="titan-surface p-6 rounded-xl border border-titan-border border-t-2 border-t-red-500"
          >
            <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
              <ShieldAlert className="w-5 h-5 text-red-500" />
              Risk Mitigation
            </h3>
            <div className="space-y-4">
              {Object.entries(finalReport.risks_and_mitigations || {}).map(([risk, mitigation]: [string, any], idx) => (
                <div key={idx} className="bg-red-500/5 p-3 rounded border border-red-500/10">
                  <div className="text-red-400 font-medium text-sm mb-1">{risk}</div>
                  <div className="text-titan-text-secondary text-xs">{mitigation as string}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

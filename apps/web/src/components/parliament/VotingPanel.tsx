'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useSessionStore } from '@/store/useSessionStore';
import { CheckCircle2, AlertCircle } from 'lucide-react';

export function VotingPanel() {
  const { votes, phase } = useSessionStore();

  if (votes.length === 0 && phase !== 'voting') return null;

  return (
    <div className="titan-card p-6 h-[600px] flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-titan-gold" />
          Cabinet Votes
        </h2>
        <span className="text-xs font-mono text-titan-text-muted bg-titan-surface-2 px-2 py-1 rounded">
          {votes.length} / 6 VOTES CAST
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {votes.map((vote, idx) => (
          <motion.div
            key={vote.agent_role}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.1 }}
            className="p-4 rounded-xl border border-titan-border bg-black/40 relative overflow-hidden"
          >
            <div className={`absolute top-0 left-0 w-1 h-full badge-${vote.agent_role}`}></div>
            
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                {vote.agent_role.replace('_', ' ')}
              </span>
              <span className={`text-xs font-mono px-2 py-0.5 rounded ${vote.confidence_score >= 80 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                {vote.confidence_score.toFixed(0)}% CONFIDENCE
              </span>
            </div>
            
            <div className="text-sm font-semibold text-titan-blue-light mb-2">
              "{vote.voted_option}"
            </div>
            
            <p className="text-xs text-titan-text-secondary leading-relaxed">
              {vote.justification}
            </p>
          </motion.div>
        ))}

        {phase === 'voting' && votes.length < 6 && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-8 rounded-xl border border-titan-border border-dashed flex flex-col items-center justify-center text-center opacity-50"
          >
            <AlertCircle className="w-6 h-6 text-titan-text-muted mb-2 animate-pulse" />
            <span className="text-xs text-titan-text-muted font-mono uppercase">Awaiting remaining votes...</span>
          </motion.div>
        )}
      </div>
    </div>
  );
}

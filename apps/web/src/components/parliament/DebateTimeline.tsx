'use client';

import React, { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSessionStore } from '@/store/useSessionStore';
import { MessageSquare, ShieldAlert, ShieldCheck, Activity } from 'lucide-react';

export function DebateTimeline() {
  const { debates, phase } = useSessionStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [debates]);

  if (debates.length === 0 && phase !== 'debating') return null;

  return (
    <div className="titan-card flex flex-col h-[600px] overflow-hidden">
      <div className="p-4 border-b border-titan-border flex items-center justify-between glass z-10">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-titan-blue-light" />
          Live Debate Transcript
        </h2>
        <span className="text-xs font-mono text-titan-text-muted">
          Round {debates.length > 0 ? debates[debates.length - 1].round_number : 1}
        </span>
      </div>

      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth"
      >
        <AnimatePresence initial={false}>
          {debates.map((debate, idx) => {
            const isAttack = debate.phase === 'opposition_attack';
            const isDefense = debate.phase === 'rebuttal';
            const isPresentation = debate.phase === 'presentation';
            
            return (
              <motion.div
                key={`${debate.agent_role}-${idx}`}
                initial={{ opacity: 0, x: -20, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                className="flex gap-4"
              >
                <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center badge-${debate.agent_role} border`}>
                  {isAttack ? <ShieldAlert className="w-5 h-5" /> : 
                   isDefense ? <ShieldCheck className="w-5 h-5" /> : 
                   <Activity className="w-5 h-5" />}
                </div>
                
                <div className={`flex-1 rounded-xl p-4 border ${isAttack ? 'bg-red-500/5 border-red-500/20' : 'titan-surface-2 border-titan-border'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-white uppercase tracking-wider">
                      {debate.agent_role.replace('_', ' ')}
                    </span>
                    <span className="text-[10px] font-mono text-titan-text-muted uppercase">
                      {debate.phase}
                    </span>
                  </div>
                  <p className="text-sm text-titan-text-secondary whitespace-pre-wrap leading-relaxed">
                    {debate.argument}
                  </p>
                  
                  {(debate.attacking_roles?.length > 0 || debate.defending_positions?.length > 0) && (
                    <div className="mt-3 pt-3 border-t border-titan-border/50 flex flex-wrap gap-2">
                      {debate.attacking_roles?.map((r: string) => (
                        <span key={r} className="text-[10px] px-2 py-1 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                          Targets: {r.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
          
          {(phase === 'debating' || phase === 'analyzing') && (
            <motion.div 
              key="typing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-4 opacity-50"
            >
              <div className="w-10 h-10 rounded-full bg-titan-surface border border-titan-border flex items-center justify-center">
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-titan-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-titan-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-titan-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

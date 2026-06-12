'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSessionStore } from '@/store/useSessionStore';
import { Shield, BrainCircuit, Landmark, Factory, Users as UsersIcon, Leaf, AlertTriangle } from 'lucide-react';

const agentConfig: Record<string, { icon: React.ElementType, name: string }> = {
  prime_minister: { icon: Landmark, name: "Prime Minister" },
  economic_minister: { icon: BrainCircuit, name: "Economic Minister" },
  technology_minister: { icon: Shield, name: "Technology Minister" },
  infrastructure_minister: { icon: Factory, name: "Infrastructure Minister" },
  citizen_minister: { icon: UsersIcon, name: "Citizen Minister" },
  environment_minister: { icon: Leaf, name: "Environment Minister" },
  opposition_minister: { icon: AlertTriangle, name: "Opposition Minister" },
};

export function AgentCards() {
  const { analyses, phase } = useSessionStore();

  const isAnalyzing = phase === 'analyzing';

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4 mb-8">
      {Object.entries(agentConfig).map(([role, config], idx) => {
        const analysis = analyses.find(a => a.agent_role === role);
        const Icon = config.icon;
        const isActive = isAnalyzing || analysis;

        return (
          <motion.div
            key={role}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`relative p-4 rounded-xl border flex flex-col items-center justify-center text-center overflow-hidden transition-all duration-500
              ${isActive ? 'titan-surface-2 border-titan-border' : 'bg-black/20 border-titan-border/30 opacity-50'}
              ${isAnalyzing && !analysis && role !== 'prime_minister' ? 'border-titan-blue/50 titan-glow' : ''}
            `}
          >
            {/* Background Glow */}
            <div className={`absolute inset-0 opacity-10 bg-gradient-to-t from-transparent badge-${role}`}></div>

            {/* Pulse Ring if analyzing */}
            {isAnalyzing && !analysis && role !== 'prime_minister' && (
              <span className="absolute inset-0 rounded-xl border-2 border-titan-blue opacity-20 animate-ping"></span>
            )}

            <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-3 badge-${role} border`}>
              <Icon className="w-6 h-6" />
            </div>
            
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-1 leading-tight">
              {config.name.replace(' Minister', '\nMinister')}
            </h3>

            <div className="mt-2 h-4 flex items-center justify-center">
              <AnimatePresence mode="wait">
                {analysis ? (
                  <motion.span 
                    key="done"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="text-[10px] text-green-400 font-mono uppercase"
                  >
                    Analysis Complete
                  </motion.span>
                ) : isAnalyzing && role !== 'prime_minister' ? (
                  <motion.span 
                    key="loading"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="text-[10px] text-titan-blue-light font-mono uppercase typing-cursor"
                  >
                    Processing
                  </motion.span>
                ) : (
                  <span className="text-[10px] text-titan-text-muted font-mono uppercase">
                    Standby
                  </span>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

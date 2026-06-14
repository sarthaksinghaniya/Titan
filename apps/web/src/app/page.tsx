'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Network, ArrowRight, Loader2, Cpu } from 'lucide-react';
import { sessionsApi } from '@/lib/api-client';
import { useSessionStore } from '@/store/useSessionStore';

export default function Home() {
  const router = useRouter();
  const { setProjectId, setProblemText, resetSession } = useSessionStore();
  
  const [problem, setProblem] = useState('');
  const [context, setContext] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!problem.trim() || problem.length < 20) {
      setError('Problem statement must be at least 20 characters.');
      return;
    }

    setLoading(true);
    setError(null);
    resetSession(); // Clear any previous session

    try {
      const data = await sessionsApi.create({
        problem,
        context: context.trim() || undefined,
      });

      setProblemText(problem);
      setProjectId(data.session_id);
      router.push('/parliament');
    } catch (err: any) {
      console.error(err);
      if (!err.response) {
        setError('Backend offline: Could not connect to the TITAN API. Please ensure the backend server is running.');
      } else {
        setError(err.response?.data?.detail || 'Failed to initialize TITAN session');
      }
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh]">
      <motion.div 
        className="text-center max-w-3xl mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-titan-blue/30 bg-titan-blue/10 text-titan-blue-light mb-6 text-sm font-medium">
          <Network className="w-4 h-4" />
          <span>Multi-Agent Governance Engine</span>
        </div>
        <h1 className="text-5xl font-black mb-6 tracking-tight text-white">
          Simulate <span className="gradient-text">Policy Impact</span> Before It Happens.
        </h1>
        <p className="text-lg text-titan-text-secondary leading-relaxed">
          Input a complex societal challenge. Our autonomous AI cabinet will analyze, debate, attack, defend, and simulate outcomes across diverse futures to synthesize the optimal strategy.
        </p>
      </motion.div>

      <motion.form 
        onSubmit={handleSubmit}
        className="w-full max-w-2xl titan-card p-1 glass relative overflow-hidden"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-titan-blue/5 to-titan-gold/5 pointer-events-none"></div>
        <div className="relative bg-titan-surface/80 rounded-[14px] p-8 z-10">
          <div className="mb-6">
            <label className="block text-sm font-semibold text-white mb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-titan-blue-light" />
              Core Problem Statement
            </label>
            <textarea
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              placeholder="e.g., The nation needs to transition its energy grid to 100% renewables by 2035 without causing economic collapse or energy poverty."
              className="w-full h-32 bg-black/40 border border-titan-border rounded-md p-4 text-white placeholder:text-titan-text-muted focus:outline-none focus:border-titan-blue/50 focus:ring-1 focus:ring-titan-blue/50 transition-all resize-none"
              disabled={loading}
            />
          </div>

          <div className="mb-8">
            <label className="block text-sm font-semibold text-white mb-2">
              Context & Constraints <span className="text-titan-text-muted font-normal">(Optional)</span>
            </label>
            <input
              type="text"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="e.g., Current grid is 60% fossil fuels. Budget deficit is at 3%."
              className="w-full bg-black/40 border border-titan-border rounded-md p-4 text-white placeholder:text-titan-text-muted focus:outline-none focus:border-titan-blue/50 focus:ring-1 focus:ring-titan-blue/50 transition-all"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-md text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 bg-white text-black px-8 py-3 rounded-md font-bold hover:bg-gray-200 transition-colors disabled:opacity-70 disabled:cursor-not-allowed group"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Initializing Core...
                </>
              ) : (
                <>
                  Engage Ministers
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>
        </div>
      </motion.form>
    </div>
  );
}

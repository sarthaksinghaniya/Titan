'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useSessionStore } from '@/store/useSessionStore';
import { AgentCards } from '@/components/parliament/AgentCards';
import { DebateTimeline } from '@/components/parliament/DebateTimeline';
import { VotingPanel } from '@/components/parliament/VotingPanel';
import { Network } from 'lucide-react';

export default function ParliamentPage() {
  const router = useRouter();
  const { projectId, phase } = useSessionStore();

  useEffect(() => {
    if (!projectId) {
      router.push('/');
    } else if (phase === 'simulating' || phase === 'synthesizing' || phase === 'completed') {
      // Auto transition to simulation when backend reaches it
      setTimeout(() => router.push('/simulation'), 2000);
    }
  }, [projectId, phase, router]);

  if (!projectId) return null;

  return (
    <div className="h-full flex flex-col">
      <div className="mb-8">
        <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
          <Network className="w-8 h-8 text-titan-blue" />
          Live Parliament Session
        </h1>
        <p className="text-titan-text-secondary mt-2">
          Ministers are actively analyzing the problem and generating independent policy vectors.
        </p>
      </div>

      <AgentCards />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        <div className="lg:col-span-2">
          <DebateTimeline />
        </div>
        <div className="lg:col-span-1">
          <VotingPanel />
        </div>
      </div>
    </div>
  );
}

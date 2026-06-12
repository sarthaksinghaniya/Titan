'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSessionStore } from '@/store/useSessionStore';
import { DecisionReport } from '@/components/report/DecisionReport';
import { FileText } from 'lucide-react';

export default function ReportPage() {
  const router = useRouter();
  const { projectId, phase } = useSessionStore();

  useEffect(() => {
    if (!projectId) {
      router.push('/');
    }
  }, [projectId, router]);

  if (!projectId) return null;

  return (
    <div className="h-full flex flex-col pb-20">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
            <FileText className="w-8 h-8 text-titan-gold" />
            Final Decision Report
          </h1>
          <p className="text-titan-text-secondary mt-2">
            The binding policy directive synthesized by the Prime Minister agent.
          </p>
        </div>
        
        {phase === 'completed' && (
          <button 
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-titan-surface-2 hover:bg-white/10 border border-titan-border rounded-md text-sm font-bold text-white transition-colors"
          >
            Start New Session
          </button>
        )}
      </div>

      <DecisionReport />
    </div>
  );
}

'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSessionStore } from '@/store/useSessionStore';
import { SimulationCharts } from '@/components/simulation/SimulationCharts';
import { ActivitySquare } from 'lucide-react';

export default function SimulationPage() {
  const router = useRouter();
  const { projectId, phase } = useSessionStore();

  useEffect(() => {
    if (!projectId) {
      router.push('/');
    } else if (phase === 'completed') {
      setTimeout(() => router.push('/report'), 3000);
    }
  }, [projectId, phase, router]);

  if (!projectId) return null;

  return (
    <div className="h-full flex flex-col">
      <div className="mb-8">
        <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
          <ActivitySquare className="w-8 h-8 text-titan-blue" />
          Future Simulation Engine
        </h1>
        <p className="text-titan-text-secondary mt-2">
          Stress-testing the winning policy vector against four divergent future scenarios.
        </p>
      </div>

      <SimulationCharts />
    </div>
  );
}

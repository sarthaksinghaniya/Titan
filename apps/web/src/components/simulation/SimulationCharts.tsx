'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useSessionStore } from '@/store/useSessionStore';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { Activity } from 'lucide-react';

const COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ec4899'];

export function SimulationCharts() {
  const { simulations, phase } = useSessionStore();

  if (simulations.length === 0 && phase !== 'simulating') return null;
  if (simulations.length === 0) {
    return (
      <div className="titan-card p-12 flex flex-col items-center justify-center h-[500px]">
        <Activity className="w-12 h-12 text-titan-blue animate-pulse mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">Running Future Stress Tests</h3>
        <p className="text-titan-text-secondary">Simulating winning policy across 4 diverging timelines...</p>
      </div>
    );
  }

  // Format data for Radar Chart
  const radarData = [
    { subject: 'Economic', A: 0, B: 0, C: 0, D: 0, fullMark: 100 },
    { subject: 'Environment', A: 0, B: 0, C: 0, D: 0, fullMark: 100 },
    { subject: 'Social', A: 0, B: 0, C: 0, D: 0, fullMark: 100 },
    { subject: 'Feasibility', A: 0, B: 0, C: 0, D: 0, fullMark: 100 },
  ];

  simulations.forEach((sim, idx) => {
    const key = ['A', 'B', 'C', 'D'][idx] as 'A' | 'B' | 'C' | 'D';
    radarData[0][key] = sim.economic_score;
    radarData[1][key] = sim.environmental_score;
    radarData[2][key] = sim.social_score;
    radarData[3][key] = sim.feasibility_score;
  });

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="titan-card p-6 h-[500px]"
      >
        <h3 className="text-lg font-bold text-white mb-6">Multi-Dimensional Impact Analysis</h3>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="45%" outerRadius="70%" data={radarData}>
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
            
            {simulations.map((sim, idx) => (
              <Radar
                key={sim.option_description}
                name={sim.option_description}
                dataKey={['A', 'B', 'C', 'D'][idx]}
                stroke={COLORS[idx % COLORS.length]}
                fill={COLORS[idx % COLORS.length]}
                fillOpacity={0.3}
              />
            ))}
            <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }} />
            <Tooltip contentStyle={{ backgroundColor: '#0d0d14', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
          </RadarChart>
        </ResponsiveContainer>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="titan-card p-6 h-[500px]"
      >
        <h3 className="text-lg font-bold text-white mb-6">Aggregate Composite Scores</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={simulations}
            margin={{ top: 20, right: 30, left: 0, bottom: 40 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis 
              dataKey="option_description" 
              tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }} 
              axisLine={false}
              tickLine={false}
            />
            <YAxis 
              domain={[0, 100]} 
              tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip 
              cursor={{ fill: 'rgba(255,255,255,0.02)' }}
              contentStyle={{ backgroundColor: '#0d0d14', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} 
            />
            <Bar 
              dataKey="composite_score" 
              fill="#6366f1" 
              radius={[4, 4, 0, 0]}
              barSize={40}
            />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
      
      {/* Detailed Future Cards */}
      <div className="xl:col-span-2 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mt-4">
        {simulations.map((sim, idx) => (
          <motion.div
            key={sim.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + (idx * 0.1) }}
            className="titan-surface-2 p-5 rounded-xl border border-titan-border relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 w-full h-1" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></div>
            <h4 className="font-bold text-white mb-1">{sim.option_description}</h4>
            <div className="flex items-center justify-between mb-4">
              <span className="text-2xl font-black" style={{ color: COLORS[idx % COLORS.length] }}>
                {sim.composite_score.toFixed(1)}
              </span>
              <span className={`text-[10px] font-mono px-2 py-1 rounded uppercase ${
                sim.risk_level === 'low' ? 'bg-green-500/20 text-green-400' :
                sim.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}>
                {sim.risk_level} RISK
              </span>
            </div>
            
            <div className="space-y-3">
              <div>
                <span className="text-[10px] uppercase tracking-wider text-titan-text-muted block mb-1">Key Risk</span>
                <p className="text-xs text-titan-text-secondary">{sim.key_risks[0] || 'N/A'}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase tracking-wider text-titan-text-muted block mb-1">Key Benefit</span>
                <p className="text-xs text-titan-text-secondary">{sim.key_benefits[0] || 'N/A'}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, ExternalLink, Activity } from 'lucide-react';
import { useSessionStore } from '@/store/useSessionStore';

export const EvidenceCitations = () => {
  const executiveReports = useSessionStore(state => state.executiveReports);
  
  if (!executiveReports || executiveReports.length === 0) return null;

  // Aggregate all evidence tables from the generated reports
  const allEvidence = executiveReports.reduce((acc: any[], report: any) => {
    if (report.evidence_table && Array.isArray(report.evidence_table)) {
      return [...acc, ...report.evidence_table];
    }
    return acc;
  }, []);

  // Deduplicate claims by source or claim text
  const uniqueCitations = allEvidence.filter((v, i, a) => a.findIndex(t => (t.claim === v.claim)) === i);

  if (uniqueCitations.length === 0) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
      className="titan-surface p-6 rounded-xl border border-titan-border mt-6 col-span-1 lg:col-span-3"
    >
      <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <BookOpen className="w-6 h-6 text-titan-gold" />
        Evidence Dossier & Citations
      </h3>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-titan-text-secondary">
          <thead className="text-xs text-titan-text-muted uppercase bg-black/40 border-b border-titan-border">
            <tr>
              <th className="px-4 py-3 rounded-tl-lg">ID</th>
              <th className="px-4 py-3">Verified Claim</th>
              <th className="px-4 py-3">Source Material</th>
              <th className="px-4 py-3 text-right rounded-tr-lg">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-titan-border">
            {uniqueCitations.map((citation: any, idx: number) => (
              <tr key={idx} className="hover:bg-white/5 transition-colors">
                <td className="px-4 py-4 font-mono text-titan-blue-light text-xs whitespace-nowrap">
                  {citation.evidence_id || 'EV-GEN'}
                </td>
                <td className="px-4 py-4 font-medium text-white max-w-md">
                  {citation.claim}
                </td>
                <td className="px-4 py-4 max-w-sm">
                  <div className="flex items-center gap-2">
                    <span className="truncate">{citation.source || 'TITAN Primary Analysis'}</span>
                    <ExternalLink className="w-3 h-3 text-titan-blue-light" />
                  </div>
                </td>
                <td className="px-4 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <Activity className="w-4 h-4 text-green-400" />
                    <span className="font-mono text-green-400">{citation.confidence || 95}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

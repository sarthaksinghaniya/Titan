'use client';

import React, { useMemo, Profiler } from 'react';
import { ReactFlow, Background, Controls, Node, Edge, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useSessionStore, SessionPhase } from '@/store/useSessionStore';

const onRenderCallback = (
  id: string,
  phase: "mount" | "update",
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number
) => {
  if (actualDuration > 10) { // Log renders taking longer than 10ms
    console.debug(`[Profiler] ${id} - ${phase} took ${actualDuration.toFixed(2)}ms`);
  }
};

export const WorkflowGraph = React.memo(function WorkflowGraph() {
  const phase = useSessionStore(state => state.phase);

  const getStatus = (nodePhase: string) => {
    const order = ['pending', 'researching', 'analyzing', 'debating', 'voting', 'simulating', 'synthesizing', 'black_swan', 'completed'];
    
    // Convert granular research phases to 'researching'
    let effectivePhase = phase;
    if (['validating_evidence', 'compressing_context'].includes(phase)) {
        effectivePhase = 'researching';
    }

    const currentIndex = order.indexOf(effectivePhase);
    const nodeIndex = order.indexOf(nodePhase);
    
    // Problem is always first
    if (nodePhase === 'problem') return 'completed';
    
    if (currentIndex > nodeIndex) return 'completed';
    if (currentIndex === nodeIndex) return 'active';
    return 'pending';
  };

  const nodes: Node[] = useMemo(() => [
    {
      id: 'problem',
      position: { x: 50, y: 100 },
      data: { label: 'Problem Input' },
      style: {
        background: '#0d0d14',
        color: '#fff',
        border: '1px solid #10b981',
        borderRadius: '8px',
        padding: '10px 20px',
        fontWeight: 'bold',
      },
    },
    {
      id: 'researching',
      position: { x: 250, y: 100 },
      data: { label: 'Knowledge Retrieval' },
      style: {
        background: '#0d0d14',
        color: '#fff',
        border: getStatus('researching') === 'active' ? '2px solid #a855f7' : getStatus('researching') === 'completed' ? '1px solid #10b981' : '1px solid #333',
        boxShadow: getStatus('researching') === 'active' ? '0 0 15px rgba(168,85,247,0.5)' : 'none',
        borderRadius: '8px',
        padding: '10px 20px',
        opacity: getStatus('researching') === 'pending' ? 0.5 : 1,
      },
    },
    {
      id: 'analyzing',
      position: { x: 450, y: 100 },
      data: { label: 'Ministers Analysis' },
      style: {
        background: '#0d0d14',
        color: '#fff',
        border: getStatus('analyzing') === 'active' ? '2px solid #6366f1' : getStatus('analyzing') === 'completed' ? '1px solid #10b981' : '1px solid #333',
        boxShadow: getStatus('analyzing') === 'active' ? '0 0 15px rgba(99,102,241,0.5)' : 'none',
        borderRadius: '8px',
        padding: '10px 20px',
        opacity: getStatus('analyzing') === 'pending' ? 0.5 : 1,
      },
    },
    {
      id: 'debating',
      position: { x: 650, y: 100 },
      data: { label: 'Debate Round' },
      style: {
        background: '#0d0d14',
        color: '#fff',
        border: getStatus('debating') === 'active' ? '2px solid #f59e0b' : getStatus('debating') === 'completed' ? '1px solid #10b981' : '1px solid #333',
        boxShadow: getStatus('debating') === 'active' ? '0 0 15px rgba(245,158,11,0.5)' : 'none',
        borderRadius: '8px',
        padding: '10px 20px',
        opacity: getStatus('debating') === 'pending' ? 0.5 : 1,
      },
    },
    {
      id: 'voting',
      position: { x: 850, y: 100 },
      data: { label: 'Voting Phase' },
      style: {
        background: '#0d0d14',
        color: '#fff',
        border: getStatus('voting') === 'active' ? '2px solid #ec4899' : getStatus('voting') === 'completed' ? '1px solid #10b981' : '1px solid #333',
        boxShadow: getStatus('voting') === 'active' ? '0 0 15px rgba(236,72,153,0.5)' : 'none',
        borderRadius: '8px',
        padding: '10px 20px',
        opacity: getStatus('voting') === 'pending' ? 0.5 : 1,
      },
    },
    {
      id: 'simulating',
      position: { x: 1050, y: 100 },
      data: { label: 'Simulation Engine' },
      style: {
        background: '#0d0d14',
        color: '#fff',
        border: getStatus('simulating') === 'active' ? '2px solid #0ea5e9' : getStatus('simulating') === 'completed' ? '1px solid #10b981' : '1px solid #333',
        boxShadow: getStatus('simulating') === 'active' ? '0 0 15px rgba(14,165,233,0.5)' : 'none',
        borderRadius: '8px',
        padding: '10px 20px',
        opacity: getStatus('simulating') === 'pending' ? 0.5 : 1,
      },
    },
    {
      id: 'synthesizing',
      position: { x: 1250, y: 100 },
      data: { label: 'Final Decision' },
      style: {
        background: '#0d0d14',
        color: '#fff',
        border: getStatus('synthesizing') === 'active' ? '2px solid #f59e0b' : getStatus('synthesizing') === 'completed' ? '1px solid #10b981' : '1px solid #333',
        boxShadow: getStatus('synthesizing') === 'active' ? '0 0 15px rgba(245,158,11,0.5)' : 'none',
        borderRadius: '8px',
        padding: '10px 20px',
        opacity: getStatus('synthesizing') === 'pending' ? 0.5 : 1,
      },
    },
    {
      id: 'black_swan',
      position: { x: 1450, y: 100 },
      data: { label: 'Black Swan Engine' },
      style: {
        background: '#0d0d14',
        color: '#fff',
        border: getStatus('black_swan') === 'active' ? '2px solid #ef4444' : getStatus('black_swan') === 'completed' ? '1px solid #10b981' : '1px solid #333',
        boxShadow: getStatus('black_swan') === 'active' ? '0 0 15px rgba(239,68,68,0.5)' : 'none',
        borderRadius: '8px',
        padding: '10px 20px',
        opacity: getStatus('black_swan') === 'pending' ? 0.5 : 1,
      },
    },
  ], [phase]);

  const edges: Edge[] = useMemo(() => [
    {
      id: 'e1',
      source: 'problem',
      target: 'researching',
      animated: getStatus('researching') === 'active',
      style: { stroke: getStatus('researching') !== 'pending' ? '#10b981' : '#333', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: getStatus('researching') !== 'pending' ? '#10b981' : '#333' }
    },
    {
      id: 'e2',
      source: 'researching',
      target: 'analyzing',
      animated: getStatus('analyzing') === 'active',
      style: { stroke: getStatus('analyzing') !== 'pending' ? '#10b981' : '#333', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: getStatus('analyzing') !== 'pending' ? '#10b981' : '#333' }
    },
    {
      id: 'e3',
      source: 'analyzing',
      target: 'debating',
      animated: getStatus('debating') === 'active',
      style: { stroke: getStatus('debating') !== 'pending' ? '#10b981' : '#333', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: getStatus('debating') !== 'pending' ? '#10b981' : '#333' }
    },
    {
      id: 'e4',
      source: 'debating',
      target: 'voting',
      animated: getStatus('voting') === 'active',
      style: { stroke: getStatus('voting') !== 'pending' ? '#10b981' : '#333', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: getStatus('voting') !== 'pending' ? '#10b981' : '#333' }
    },
    {
      id: 'e5',
      source: 'voting',
      target: 'simulating',
      animated: getStatus('simulating') === 'active',
      style: { stroke: getStatus('simulating') !== 'pending' ? '#10b981' : '#333', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: getStatus('simulating') !== 'pending' ? '#10b981' : '#333' }
    },
    {
      id: 'e6',
      source: 'simulating',
      target: 'synthesizing',
      animated: getStatus('synthesizing') === 'active',
      style: { stroke: getStatus('synthesizing') !== 'pending' ? '#10b981' : '#333', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: getStatus('synthesizing') !== 'pending' ? '#10b981' : '#333' }
    },
    {
      id: 'e7',
      source: 'synthesizing',
      target: 'black_swan',
      animated: getStatus('black_swan') === 'active',
      style: { stroke: getStatus('black_swan') !== 'pending' ? '#10b981' : '#333', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: getStatus('black_swan') !== 'pending' ? '#10b981' : '#333' }
    },
  ], [phase]);

  return (
    <Profiler id="WorkflowGraph" onRender={onRenderCallback}>
      <div className="w-full h-[180px] titan-card overflow-hidden mb-8 relative">
        <div className="absolute top-3 left-4 z-10 text-xs font-mono font-bold text-titan-text-secondary uppercase">
          Graph Execution Trace
        </div>
        <ReactFlow 
          nodes={nodes} 
          edges={edges} 
          fitView 
          fitViewOptions={{ padding: 0.2 }}
          className="bg-black/20"
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          zoomOnScroll={false}
          panOnDrag={false}
        >
          <Background color="#333" gap={16} size={1} />
        </ReactFlow>
      </div>
    </Profiler>
  );
});

"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Crown,
  ArrowRight,
  Brain,
  Vote,
  FlaskConical,
  Zap,
  ChevronDown,
  Sparkles,
  Users,
  BarChart3,
  Shield,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { sessionsApi } from "@/lib/api-client";
import { useSessionsListStore } from "@/store/session-store";
import { MINISTER_META } from "@titan/shared-types";
import type { MinisterRole } from "@titan/shared-types";

// ─── Sample Problems ──────────────────────────────────────────
const SAMPLE_PROBLEMS = [
  "India faces a critical water scarcity crisis affecting 600 million people. Underground water tables are depleting at an alarming rate while agriculture consumes 80% of available water. How should the government address this long-term challenge?",
  "Unemployment among youth (ages 18-35) has reached 35% in urban areas due to automation and AI displacement. Traditional manufacturing jobs are disappearing faster than new ones are being created.",
  "Air pollution in major cities has reached 10x the WHO safe limit. Respiratory diseases account for 30% of hospital admissions. Industrial emissions and vehicle exhaust are the primary causes.",
  "Digital divide is growing — 40% of rural population lacks internet access, blocking their participation in the digital economy. Remote education and healthcare remain inaccessible.",
];

const FLOW_STEPS = [
  { icon: Brain, label: "AI Analysis", desc: "6 ministers independently analyze", color: "text-indigo-400" },
  { icon: Users, label: "Debate", desc: "Ministers argue and counter-argue", color: "text-amber-400" },
  { icon: Vote, label: "Voting", desc: "Democratic vote with justification", color: "text-pink-400" },
  { icon: FlaskConical, label: "Simulation", desc: "Synthetic stress-testing", color: "text-sky-400" },
  { icon: Crown, label: "Final Policy", desc: "PM synthesizes winning strategy", color: "text-amber-400" },
];

const MINISTER_ROLES: MinisterRole[] = [
  "economic_minister",
  "technology_minister",
  "infrastructure_minister",
  "citizen_minister",
  "environment_minister",
  "opposition_minister",
];

export default function HomePage() {
  const router = useRouter();
  const { addSession } = useSessionsListStore();

  const [problem, setProblem] = useState("");
  const [context, setContext] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showContext, setShowContext] = useState(false);
  const charCount = problem.length;
  const maxChars = 2000;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!problem.trim() || problem.trim().length < 20) {
      toast.error("Please describe the problem in at least 20 characters.");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await sessionsApi.create({
        problem: problem.trim(),
        context: context.trim() || undefined,
      });
      const newSession = await sessionsApi.get(response.session_id);
      addSession(newSession);
      toast.success("Cabinet session initiated. Ministers are assembling...");
      router.push(`/sessions/${response.session_id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create session";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function useSampleProblem(sample: string) {
    setProblem(sample);
  }

  return (
    <div className="flex flex-col min-h-screen bg-titan-bg">
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="bg-grid absolute inset-0 opacity-60" />
        <div className="orb-1 top-[-100px] left-[20%] opacity-60" />
        <div className="orb-2 bottom-[10%] right-[15%]" />
      </div>

      <div className="relative flex flex-col flex-1 px-8 py-8 max-w-4xl mx-auto w-full">
        {/* Hero Header */}
        <div className="mb-10 animate-slide-up">
          <div className="flex items-center gap-2 mb-5">
            <Badge variant="info" dot className="text-[11px]">
              <Sparkles className="size-3" />
              AI Cabinet Active — 8 Agents Ready
            </Badge>
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tight mb-3">
            What problem should the{" "}
            <span className="gradient-text">AI Cabinet</span> solve?
          </h1>
          <p className="text-base text-white/50 max-w-xl leading-relaxed">
            Describe a societal challenge. Eight AI ministers will independently analyze it,
            debate solutions, vote, run simulations, and deliver a final governance strategy.
          </p>
        </div>

        {/* Flow Steps */}
        <div className="flex items-center gap-0 mb-10 animate-slide-up" style={{ animationDelay: "100ms" }}>
          {FLOW_STEPS.map((step, i) => {
            const Icon = step.icon;
            return (
              <React.Fragment key={step.label}>
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/5">
                  <Icon className={`size-4 ${step.color} shrink-0`} />
                  <div>
                    <div className="text-xs font-semibold text-white/80">{step.label}</div>
                    <div className="text-[10px] text-white/35">{step.desc}</div>
                  </div>
                </div>
                {i < FLOW_STEPS.length - 1 && (
                  <ChevronDown className="size-3.5 text-white/20 rotate-[-90deg] shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Main Form */}
        <Card
          className="p-6 animate-slide-up"
          style={{ animationDelay: "200ms" } as React.CSSProperties}
          glow
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="problem-input"
                  className="text-sm font-semibold text-white/80"
                >
                  Describe the Problem
                </label>
                <span
                  className={`text-xs font-mono ${charCount > maxChars * 0.9 ? "text-amber-400" : "text-white/30"}`}
                >
                  {charCount}/{maxChars}
                </span>
              </div>
              <textarea
                id="problem-input"
                value={problem}
                onChange={(e) => setProblem(e.target.value.slice(0, maxChars))}
                rows={6}
                placeholder="e.g. India faces a critical water scarcity crisis affecting 600 million people. Underground water tables are depleting..."
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white/90 placeholder:text-white/25 transition-all duration-200 resize-none focus:outline-none focus:border-indigo-500/60 focus:bg-white/[0.07] focus:ring-1 focus:ring-indigo-500/30 hover:border-white/15"
              />
            </div>

            {/* Optional Context Toggle */}
            <button
              type="button"
              onClick={() => setShowContext(!showContext)}
              className="flex items-center gap-1.5 text-xs text-white/40 hover:text-white/70 transition-colors"
            >
              <ChevronDown
                className={`size-3.5 transition-transform duration-200 ${showContext ? "rotate-180" : ""}`}
              />
              {showContext ? "Hide" : "Add"} additional context (optional)
            </button>

            {showContext && (
              <div className="animate-fade-in">
                <textarea
                  id="context-input"
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  rows={3}
                  placeholder="Provide regional context, constraints, budget limitations, political considerations..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white/90 placeholder:text-white/25 transition-all duration-200 resize-none focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30"
                />
              </div>
            )}

            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-1.5 text-xs text-white/30">
                <Zap className="size-3 text-amber-400/60" />
                <span>Powered by Gemini AI + LangGraph</span>
              </div>
              <Button
                type="submit"
                variant="primary"
                size="lg"
                id="submit-problem-btn"
                isLoading={isSubmitting}
                disabled={problem.trim().length < 20}
                rightIcon={<ArrowRight className="size-4" />}
                className="bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400"
              >
                Convene Cabinet
              </Button>
            </div>
          </form>
        </Card>

        {/* Sample Problems */}
        <div className="mt-8 animate-slide-up" style={{ animationDelay: "300ms" } as React.CSSProperties}>
          <p className="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">
            Try a sample problem
          </p>
          <div className="grid grid-cols-1 gap-2">
            {SAMPLE_PROBLEMS.map((sample, i) => (
              <button
                key={i}
                id={`sample-problem-${i}`}
                onClick={() => useSampleProblem(sample)}
                className="text-left px-4 py-3 rounded-lg bg-white/[0.02] border border-white/5 hover:bg-white/[0.05] hover:border-white/10 transition-all duration-150 group"
              >
                <p className="text-xs text-white/50 group-hover:text-white/70 transition-colors line-clamp-2 leading-relaxed">
                  {sample}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Ministers Preview */}
        <div className="mt-8 animate-slide-up" style={{ animationDelay: "400ms" } as React.CSSProperties}>
          <p className="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">
            Your AI Cabinet
          </p>
          <div className="grid grid-cols-3 gap-2">
            {MINISTER_ROLES.map((role) => {
              const meta = MINISTER_META[role];
              return (
                <div
                  key={role}
                  className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg bg-white/[0.02] border border-white/5"
                >
                  <div
                    className="size-7 rounded-lg flex items-center justify-center shrink-0"
                    style={{ background: `${meta.color}18` }}
                  >
                    <span className="text-xs" style={{ color: meta.color }}>✦</span>
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-white/70 truncate">{meta.title}</div>
                    <div className="text-[10px] text-white/30 truncate">{meta.focus_areas[0]}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-4 mt-8 pb-8 animate-slide-up" style={{ animationDelay: "500ms" } as React.CSSProperties}>
          {[
            { icon: Brain, value: "8", label: "AI Agents", color: "text-indigo-400" },
            { icon: BarChart3, value: "2", label: "Debate Rounds", color: "text-amber-400" },
            { icon: Shield, value: "100%", label: "Synthetic Data", color: "text-emerald-400" },
          ].map(({ icon: Icon, value, label, color }) => (
            <div key={label} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/[0.02] border border-white/5">
              <Icon className={`size-5 ${color}`} />
              <div>
                <div className="text-base font-bold text-white">{value}</div>
                <div className="text-xs text-white/40">{label}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

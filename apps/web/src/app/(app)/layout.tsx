import type { Metadata } from "next";
import { Sidebar } from "@/components/layout/sidebar";

export const metadata: Metadata = {
  title: "TITAN — Governance Intelligence",
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-titan-bg">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">{children}</div>
    </div>
  );
}

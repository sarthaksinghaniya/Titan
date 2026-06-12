"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "glass" | "bordered";
  hover?: boolean;
  glow?: boolean;
}

export function Card({
  variant = "default",
  hover = false,
  glow = false,
  className,
  children,
  ...props
}: CardProps) {
  const variants = {
    default: "titan-card",
    glass: "glass rounded-2xl",
    bordered: "bg-transparent border border-white/10 rounded-2xl",
  };

  return (
    <div
      className={cn(
        variants[variant],
        hover && "cursor-pointer",
        glow && "titan-glow",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("p-5 border-b border-white/5", className)} {...props}>
      {children}
    </div>
  );
}

export function CardContent({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("p-5", className)} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("p-5 border-t border-white/5", className)} {...props}>
      {children}
    </div>
  );
}

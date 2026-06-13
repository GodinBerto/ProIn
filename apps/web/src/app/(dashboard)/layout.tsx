"use client";
import LayoutContainer from "@/components/layout/LayoutContainer";
import { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <LayoutContainer>{children}</LayoutContainer>;
}

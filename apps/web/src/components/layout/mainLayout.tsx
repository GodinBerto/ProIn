"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";
import { AuthSessionProvider } from "../providers/session-provider";

export default function MainLayout({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );
  return (
    <QueryClientProvider client={client}>
      <AuthSessionProvider>{children}</AuthSessionProvider>
    </QueryClientProvider>
  );
}

"use client";

import { fetchCurrentUser } from "@/lib/api";
import { useUserStore } from "@/stores/user-store";
import { signOut, useSession } from "next-auth/react";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const { user, setUser, clearUser } = useUserStore();
  const [isVerifying, setIsVerifying] = useState(true);

  useEffect(() => {
    if (status === "loading") {
      return;
    }

    if (status !== "authenticated") {
      setIsVerifying(false);
      return;
    }

    const accessToken = session?.accessToken;

    if (!accessToken) {
      clearUser();
      void signOut({ callbackUrl: "/login" });
      return;
    }

    let cancelled = false;

    fetchCurrentUser(accessToken)
      .then((profile) => {
        if (cancelled) {
          return;
        }

        setUser(profile);
        setIsVerifying(false);
      })
      .catch(() => {
        if (cancelled) {
          return;
        }

        clearUser();
        void signOut({ callbackUrl: "/login" });
      });

    return () => {
      cancelled = true;
    };
  }, [status, session?.accessToken, setUser, clearUser]);

  if (status === "loading" || isVerifying) {
    return <div className="p-6">Loading dashboard...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      {user ? (
        <p className="mt-2 text-muted-foreground">
          Welcome back, {user.full_name ?? user.email}
        </p>
      ) : null}
    </div>
  );
}

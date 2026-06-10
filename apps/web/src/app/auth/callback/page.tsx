"use client";

import { Loader2 } from "@repo/ui";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

function parseHashParams(hash: string) {
  const params = new URLSearchParams(hash.replace(/^#/, ""));
  return {
    accessToken: params.get("access_token"),
    type: params.get("type"),
    error: params.get("error_description") ?? params.get("error"),
  };
}

export default function AuthCallbackPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const { accessToken, type, error: hashError } = parseHashParams(
      window.location.hash,
    );

    if (hashError) {
      setError(hashError);
      return;
    }

    if (!accessToken) {
      setError("Missing access token. Open the link from your email again.");
      return;
    }

    if (type && type !== "magiclink" && type !== "signup") {
      setError("Unsupported authentication link.");
      return;
    }

    void signIn("credentials", {
      redirect: false,
      accessToken,
    })
      .then((result) => {
        if (result?.error) {
          setError(result.error);
          return;
        }

        router.replace("/dashboard");
      })
      .catch(() => {
        setError("Failed to complete sign in.");
      });
  }, [router]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <div className="max-w-sm text-center">
          <h1 className="text-xl font-semibold">Sign in failed</h1>
          <p className="mt-2 text-sm text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin" />
        Completing sign in...
      </div>
    </div>
  );
}

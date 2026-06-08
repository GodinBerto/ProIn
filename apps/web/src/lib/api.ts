import type { UserProfile } from "@/types/user";

const backendUrl =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:5236";

export async function fetchCurrentUser(
  accessToken: string,
): Promise<UserProfile> {
  const response = await fetch(`${backendUrl}/api/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch current user");
  }

  return response.json();
}

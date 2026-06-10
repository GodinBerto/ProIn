import type { UserProfile } from "@/types/user";

const backendUrl =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:5236";

const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? "http://127.0.0.1:3005";

export type AuthResponse = {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
  expires_in: number;
  is_new_user: boolean;
  user: {
    id: string;
    email: string;
    full_name?: string | null;
    avatar_url?: string | null;
  };
};

type ApiError = {
  detail?: string;
};

async function parseApiError(response: Response): Promise<string> {
  const error = (await response.json().catch(() => ({}))) as ApiError;
  return error.detail ?? "Request failed";
}

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

export async function registerUser(
  email: string,
  password: string,
): Promise<AuthResponse> {
  const response = await fetch(`${backendUrl}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}

export async function loginUser(
  email: string,
  password: string,
): Promise<AuthResponse> {
  const response = await fetch(`${backendUrl}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}

export async function sendMagicLink(email: string): Promise<{ message: string }> {
  const response = await fetch(`${backendUrl}/api/auth/magic-link`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      redirect_to: `${appUrl}/auth/callback`,
    }),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}

export async function syncAuthSession(accessToken: string): Promise<AuthResponse> {
  const response = await fetch(`${backendUrl}/api/auth/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access_token: accessToken }),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}

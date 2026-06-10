import { authOptions as baseAuthOptions } from "@repo/auth";
import NextAuth, { type NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

import {
  loginUser,
  syncAuthSession,
  type AuthResponse,
} from "@/lib/api";

const backendUrl = process.env.BACKEND_URL ?? "http://127.0.0.1:5236";

type GoogleBackendAuthResponse = {
  access_token: string;
  user: {
    id: string;
    email: string;
    full_name?: string | null;
    avatar_url?: string | null;
  };
  is_new_user: boolean;
};

type GoogleProfile = {
  email?: string | null;
  name?: string | null;
  picture?: string | null;
};

const googleAuthByEmail = new Map<string, GoogleBackendAuthResponse>();

async function syncGoogleUserWithBackend(
  profile: GoogleProfile,
  account: { id_token?: string | null },
): Promise<GoogleBackendAuthResponse> {
  const response = await fetch(`${backendUrl}/api/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: profile.email,
      full_name: profile.name,
      avatar_url: profile.picture,
      id_token: account.id_token,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail ?? "Failed to sync Google user with backend");
  }

  return response.json();
}

function toCredentialsUser(data: AuthResponse) {
  return {
    id: data.user.id,
    email: data.user.email,
    name: data.user.full_name ?? data.user.email,
    image: data.user.avatar_url ?? null,
    accessToken: data.access_token,
    isNewUser: data.is_new_user,
  };
}

const authOptions: NextAuthOptions = {
  ...baseAuthOptions,
  providers: [
    ...baseAuthOptions.providers,
    CredentialsProvider({
      id: "credentials",
      name: "Email",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
        accessToken: { label: "Access Token", type: "text" },
      },
      async authorize(credentials) {
        try {
          if (credentials?.accessToken) {
            const data = await syncAuthSession(credentials.accessToken);
            return toCredentialsUser(data);
          }

          if (!credentials?.email || !credentials?.password) {
            throw new Error("Email and password are required.");
          }

          const data = await loginUser(credentials.email, credentials.password);
          return toCredentialsUser(data);
        } catch (error) {
          throw new Error(
            error instanceof Error ? error.message : "Authentication failed.",
          );
        }
      },
    }),
  ],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    ...baseAuthOptions.callbacks,
    async signIn({ account, profile }) {
      if (account?.provider !== "google") {
        return true;
      }

      const googleProfile = profile as GoogleProfile | undefined;
      if (!googleProfile?.email) {
        return false;
      }

      try {
        const data = await syncGoogleUserWithBackend(googleProfile, account);
        googleAuthByEmail.set(googleProfile.email, data);
        return true;
      } catch (error) {
        console.error("Google backend sync failed:", error);
        return false;
      }
    },
    async jwt({ token, account, profile, user }) {
      if (account?.provider === "google" && profile?.email) {
        const data = googleAuthByEmail.get(profile.email);
        googleAuthByEmail.delete(profile.email);

        if (data) {
          token.sub = data.user.id;
          token.accessToken = data.access_token;
          token.isNewUser = data.is_new_user;
        }
      }

      if (account?.provider === "credentials" && user) {
        token.sub = user.id;
        token.accessToken = user.accessToken as string | undefined;
        token.isNewUser = user.isNewUser as boolean | undefined;
      }

      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub!;
        session.accessToken = token.accessToken as string | undefined;
      }

      return session;
    },
  },
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };

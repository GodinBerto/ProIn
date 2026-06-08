import { authOptions as baseAuthOptions } from "@repo/auth";
import NextAuth, { type NextAuthOptions } from "next-auth";

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

const authOptions: NextAuthOptions = {
  ...baseAuthOptions,
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
    async jwt({ token, account, profile }) {
      if (account?.provider === "google" && profile?.email) {
        const data = googleAuthByEmail.get(profile.email);
        googleAuthByEmail.delete(profile.email);

        if (data) {
          token.sub = data.user.id;
          token.accessToken = data.access_token;
          token.isNewUser = data.is_new_user;
        }
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

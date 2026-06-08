import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { UserProfile } from "@/types/user";

type UserState = {
  user: UserProfile | null;
  setUser: (user: UserProfile) => void;
  clearUser: () => void;
};

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      setUser: (user) => set({ user }),
      clearUser: () => set({ user: null }),
    }),
    {
      name: "proin-user",
    },
  ),
);

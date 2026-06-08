import NextAuth from "next-auth";
import { authOptions } from "./auth";

export const handler = NextAuth(authOptions);

export { authOptions };

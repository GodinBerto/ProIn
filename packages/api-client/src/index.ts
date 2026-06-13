// lib/api.ts
import { ApiClient } from "./client/apiClient";

const backendUrl = "http://127.0.0.1:5236//api/";

export const api = new ApiClient(backendUrl, {
  getAccessToken: () => {
    return localStorage.getItem("access_token");
  },
  onUnauthorized: () => {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  },
});

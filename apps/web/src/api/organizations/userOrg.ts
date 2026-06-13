import { api } from "@repo/api-client";

export const fetchUserOrg = async (): Promise<Organizations[]> => {
  const response = api.get<Organizations[]>("organizations/user/me");

  return response;
};

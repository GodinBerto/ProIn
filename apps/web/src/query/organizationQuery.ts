import { fetchUserOrg } from "@/api/organizations/userOrg";
import { useQuery } from "@tanstack/react-query";

const STALE_TIME_MS = 5 * 60 * 1000;

const getUserOrganizations = () => ({
  queryKey: ["user-orgs"],
  queryFn: fetchUserOrg,
  staleTime: STALE_TIME_MS,
});

export const useUserOrg = () => useQuery(getUserOrganizations());

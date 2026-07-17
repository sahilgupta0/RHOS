import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "../api";

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboardStats"],
    queryFn: () => analyticsApi.getDashboard(),
  });
}

export function useAnalyticsData(days: number = 14) {
  return useQuery({
    queryKey: ["analyticsData", days],
    queryFn: () => analyticsApi.getAnalytics(days),
  });
}

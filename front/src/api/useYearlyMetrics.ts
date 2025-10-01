import { useQuery } from "@tanstack/react-query";

type Metric = {
  name: string;
  value: number;
};

export const useYearlyMetrics = (filters?: {
  uav_type?: string;
  city?: string;
  startDate?: string;
  endDate?: string;
}) => {
  const queryKey = [
    "yearlyMetrics",
    filters?.uav_type || null,
    filters?.city || null,
    filters?.startDate || null,
    filters?.endDate || null,
  ];

  return useQuery<{ name: string; value: number }[]>({
    queryKey,
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.uav_type) params.append("uav_type", filters.uav_type);
      if (filters?.city) params.append("city", filters.city);
      if (filters?.startDate) params.append("startDate", filters.startDate);
      if (filters?.endDate) params.append("endDate", filters.endDate);

      const url = `http://127.0.0.1:8000/flights/stats/yearly?${params.toString()}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Ошибка при загрузке статистики по месяцам");

      return res.json();
    },
    refetchInterval: 60000,
  });
};


export default useYearlyMetrics;
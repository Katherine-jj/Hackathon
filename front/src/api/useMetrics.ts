import { useQuery } from "@tanstack/react-query";

type Metric = {
  name: string;
  value: number;
};

export const useMetrics = () => {
  
  return useQuery<Metric[]>({
    queryKey: ["metrics"],
    queryFn: async () => {
      const res = await fetch("/flights/stats");
      if (!res.ok) throw new Error("Ошибка при загрузке статистики");
      const data = await res.json();
      return [
        { name: "За выбранный период", value: data.totalPeriod },
        { name: "За последний год", value: data.totalYear },
      ];
    },
    refetchInterval: 600, 
  });
};

import { useEffect, useState } from "react";

type Filters = {
  uav_type?: string | null;
  city?: string | null;
  startDate?: string | null; 
  endDate?: string | null;
};

export const useTopMetrics = (
  groupBy: "city" | "uav_type" | "date",
  filters?: Filters
) => {
  const [data, setData] = useState<{ name: string; value: number }[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);

    const params = new URLSearchParams({ groupBy });
    if (filters?.uav_type) params.append("uav_type", filters.uav_type);
    if (filters?.city) params.append("city", filters.city);
    if (filters?.startDate) params.append("startDate", filters.startDate);
    if (filters?.endDate) params.append("endDate", filters.endDate);

    fetch(`http://127.0.0.1:8000/flights/top?${params.toString()}`, {
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
      })
      .then((rows: any[]) => {
        const normalized = rows.map((r) => ({
          name: r.name === null ? "—" : String(r.name),
          value: Number(r.value) || 0,
        }));
        setData(normalized);
        setIsLoading(false);
      })
      .catch((err) => {
        if (err.name === "AbortError") return;
        console.error("Ошибка useTopMetrics:", err);
        setData([]);
        setIsLoading(false);
      });

    return () => controller.abort();
  }, [
    groupBy,
    filters?.uav_type,
    filters?.city,
    filters?.startDate,
    filters?.endDate,
  ]);

  return { data, isLoading };
};

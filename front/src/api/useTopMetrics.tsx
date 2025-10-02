import { useEffect, useState, useMemo } from "react";

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

  // Мемоизируем фильтры, чтобы useEffect срабатывал только при реальном изменении значений
  const memoFilters = useMemo(() => ({
    uav_type: filters?.uav_type || undefined,
    city: filters?.city || undefined,
    startDate: filters?.startDate || undefined,
    endDate: filters?.endDate || undefined,
  }), [filters?.uav_type, filters?.city, filters?.startDate, filters?.endDate]);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);

    const params = new URLSearchParams({ groupBy });

    // Добавляем только те параметры, которые реально заданы
    if (memoFilters.uav_type) params.append("uav_type", memoFilters.uav_type);
    if (memoFilters.city) params.append("city", memoFilters.city);
    if (memoFilters.startDate) params.append("startDate", memoFilters.startDate);
    if (memoFilters.endDate) params.append("endDate", memoFilters.endDate);

    const url = `http://localhost:8000/flights/top?${params.toString()}`;
    console.log("useTopMetrics fetch URL:", url);

    fetch(url, { signal: controller.signal })
      .then(res => {
        if (!res.ok) throw new Error(`Network response was not ok: ${res.status}`);
        return res.json();
      })
      .then((rows: any[]) => {
        const normalized = rows.map(r => ({
          name: r.name ?? "—",
          value: Number(r.value) || 0,
        }));
        setData(normalized);
        setIsLoading(false);
      })
      .catch(err => {
        if (err.name === "AbortError") return;
        console.error("Ошибка useTopMetrics:", err);
        setData([]);
        setIsLoading(false);
      });

    return () => controller.abort();
  }, [groupBy, memoFilters]);

  return { data, isLoading };
};

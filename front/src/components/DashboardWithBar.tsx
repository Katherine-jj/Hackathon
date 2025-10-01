import React from "react";
import { useTopMetrics } from "../api/useTopMetrics";
import { MetricsBarChart } from "./MetricsBarChart";

type Filters = {
  startDate?: string | null;
  endDate?: string | null;
};

export const DashboardWithBar: React.FC<{ filters?: Filters }> = ({ filters }) => {
  const { data, isLoading } = useTopMetrics("city", filters);

  return (
    <div >
      <h2 className="textBlue">
        Топ регионов по активности БПЛА «{filters?.startDate && filters?.endDate ? `${filters.startDate} — ${filters.endDate}` : "выбранный период"}»
      </h2>

      {isLoading ? (
        <p>Загрузка...</p>
      ) : data.length === 0 ? (
        <p>Нет данных по выбранным параметрам</p>
      ) : (
        <div style={{ width: 500, height: 550 }}>
          <MetricsBarChart data={data} />
        </div>
      )}
    </div>
  );
};


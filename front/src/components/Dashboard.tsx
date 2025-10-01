import { useYearlyMetrics } from "../api/useYearlyMetrics";
import { MetricsChart } from "../components/MetricsChart";

type Filters = {
  uav_type?: string;
  city?: string;
  startDate?: string;
  endDate?: string;
};

export const Dashboard = ({ filters }: { filters?: Filters }) => {
  const { data, isLoading, error } = useYearlyMetrics(filters);

  const displayUav = filters?.uav_type || "БПЛА";
  const displayRegion = filters?.city || "регионе";

  if (isLoading) return <p>Загрузка...</p>;
  if (error) return <p>Ошибка при загрузке данных</p>;

  return (
    <div>
      {data && data.length > 0 ? (
        <>
          <p className="textBlue">
            Динамика полетов «{displayUav}» в «{displayRegion}»
          </p>
          
          <MetricsChart
            data={data}
            uavType={filters?.uav_type}
            region={filters?.city}
          />
        </>
      ) : (
        <p>Нет данных за выбранный период</p>
      )}
    </div>
  );
};

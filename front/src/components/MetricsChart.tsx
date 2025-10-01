import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

type Props = {
  data: { name: string; value: number }[];
  title?: string;
  subtitle?: string;
};

export const MetricsChart = ({ data, title, subtitle }: Props) => {
  return (
    <div className="DashboardStats">
        {subtitle && <p className="text-gray-500">{subtitle}</p>}
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="name"
            interval={0}
            angle={-45}
            textAnchor="end"
            height={60}
            tick={{ fontSize: 12, fill: "#374151" }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#374151" }}
            axisLine={{ stroke: "#9ca3af" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              padding: "8px",
            }}
            formatter={(value: number) => [`${value}`, "Полетов"]}
          />
          <Line
            type="monotone"
            dataKey="value"
            name="Количество полетов"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ r: 4, stroke: "#2C7FFF", strokeWidth: 2, fill: "white" }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

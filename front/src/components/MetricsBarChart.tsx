import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from "recharts";

type Props = {
  data: { name: string; value: number }[];
};

export const MetricsBarChart = ({ data }: Props) => {
  return (
    <ResponsiveContainer width="100%" height={370}>
      <BarChart
        data={data}
        margin={{ top: 20, right: 20, left: 20, bottom: 60 }}
      >
        <XAxis
          dataKey="name"
          tick={{ fill: "#3b82f6", fontSize: 12 }}
          interval={0}
          angle={-45}   
          textAnchor="end"
        />
        <YAxis />

        <Tooltip cursor={{ fill: "#f0f9ff" }} />

        <Bar dataKey="value" fill="#CCE0FF" radius={[4, 4, 0, 0]}>
          <LabelList
            dataKey="value"
            position="top"
            style={{ fill: "#2C7FFF", fontSize: 12, fontWeight: 500 }}
            formatter={(val: number) => val.toLocaleString("ru-RU")}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

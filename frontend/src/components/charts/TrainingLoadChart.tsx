import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { DailyWellness } from '../../client/types';
import { axisTickStyle, chartColors } from './chartTheme';

interface Props {
  data: DailyWellness[];
}

export function TrainingLoadChart({ data }: Props) {
  const rows = data.map((w) => ({ date: w.date, readiness: w.trainingReadinessScore }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={rows}>
        <CartesianGrid vertical={false} stroke={chartColors.grid} />
        <XAxis
          dataKey="date"
          tick={axisTickStyle}
          axisLine={{ stroke: chartColors.axis }}
          tickLine={false}
          minTickGap={30}
        />
        <YAxis
          domain={[0, 100]}
          tick={axisTickStyle}
          axisLine={{ stroke: chartColors.axis }}
          tickLine={false}
          width={32}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--surface-card)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text-primary)',
          }}
        />
        <Line
          type="monotone"
          dataKey="readiness"
          name="Training readiness"
          stroke={chartColors.seq1}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

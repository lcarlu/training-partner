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

export function VO2maxTrend({ data }: Props) {
  const rows = data
    .filter((w) => w.vo2max !== null)
    .map((w) => ({ date: w.date, vo2max: w.vo2max }));

  return (
    <ResponsiveContainer width="100%" height={200}>
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
          tick={axisTickStyle}
          axisLine={{ stroke: chartColors.axis }}
          tickLine={false}
          width={32}
          domain={['dataMin - 2', 'dataMax + 2']}
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
          dataKey="vo2max"
          name="VO2max"
          stroke={chartColors.seq1}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

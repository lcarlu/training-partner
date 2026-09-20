import {
  CartesianGrid,
  Legend,
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

export function RecoveryChart({ data }: Props) {
  const rows = data.map((w) => ({
    date: w.date,
    bodyBattery: w.bodyBatteryMax,
    sleepScore: w.sleepScore,
  }));

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
          label={{ value: 'score /100', angle: -90, position: 'insideLeft', style: axisTickStyle }}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--surface-card)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text-primary)',
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="bodyBattery"
          name="Body Battery"
          stroke={chartColors.seq1}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="sleepScore"
          name="Score de sommeil"
          stroke={chartColors.seq2}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { WeeklyVolumePoint } from '../../client/types';
import { SPORTS } from '../../client/types';
import { axisTickStyle, chartColors } from './chartTheme';

const SPORT_LABELS: Record<string, string> = {
  running: 'Course à pied',
  cycling: 'Vélo',
  swimming: 'Natation',
  strength: 'Renforcement',
};

interface Props {
  data: WeeklyVolumePoint[];
}

export function WeeklyVolumeChart({ data }: Props) {
  const rows = data.map((p) => ({ week: p.weekStart, ...p.bySport }));
  const seriesPresent = SPORTS.filter((s) => rows.some((r) => r[s] !== undefined));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={rows} barCategoryGap={6}>
        <CartesianGrid vertical={false} stroke={chartColors.grid} />
        <XAxis
          dataKey="week"
          tick={axisTickStyle}
          axisLine={{ stroke: chartColors.axis }}
          tickLine={false}
        />
        <YAxis
          tick={axisTickStyle}
          axisLine={{ stroke: chartColors.axis }}
          tickLine={false}
          width={40}
          label={{ value: 'minutes', angle: -90, position: 'insideLeft', style: axisTickStyle }}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--surface-card)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text-primary)',
          }}
        />
        {seriesPresent.length > 1 && <Legend formatter={(v) => SPORT_LABELS[v] ?? v} />}
        {seriesPresent.map((sport) => (
          <Bar
            key={sport}
            dataKey={sport}
            stackId="volume"
            name={SPORT_LABELS[sport]}
            fill={chartColors[sport]}
            radius={sport === seriesPresent[seriesPresent.length - 1] ? [4, 4, 0, 0] : 0}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

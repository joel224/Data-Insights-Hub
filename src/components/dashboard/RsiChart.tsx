
'use client';
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from 'recharts';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import type { EodDataPoint } from '@/lib/types';

interface RsiChartProps {
  data: EodDataPoint[];
}

const chartConfig = {
  rsi: {
    label: 'RSI',
    color: 'hsl(var(--chart-1))',
  },
};

export function RsiChart({ data }: RsiChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Relative Strength Index (RSI)</CardTitle>
        <CardDescription>Overbought (&gt;70) vs. Oversold (&lt;30)</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[150px] w-full">
          <BarChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={value => value}
            />
            <YAxis domain={[0, 100]} tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Bar dataKey="rsi" fill="var(--color-rsi)" radius={4} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

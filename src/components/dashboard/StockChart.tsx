
'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import type { EodDataPoint } from '@/lib/types';
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts';

interface StockChartProps {
  data: EodDataPoint[];
  symbol: string;
}

const chartConfig = {
  price: {
    label: 'Price',
    color: 'hsl(var(--chart-1))',
  },
  sma: {
    label: 'SMA',
    color: 'hsl(var(--chart-2))',
  },
};

export function StockChart({ data, symbol }: StockChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{symbol} Stock Performance</CardTitle>
        <CardDescription>Price vs. Simple Moving Average (SMA)</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <AreaChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={value => value}
            />
            <YAxis
              domain={['dataMin - 10', 'dataMax + 10']}
              tickLine={false}
              axisLine={false}
              tickMargin={8}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  indicator="line"
                  labelFormatter={(value, payload) => {
                    return payload?.[0]?.payload.date;
                  }}
                />
              }
            />
            <Area
              dataKey="price"
              type="natural"
              fill="var(--color-price)"
              fillOpacity={0.4}
              stroke="var(--color-price)"
              stackId="a"
            />
            <Area
              dataKey="sma"
              type="natural"
              fill="var(--color-sma)"
              fillOpacity={0.4}
              stroke="var(--color-sma)"
              stackId="b"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

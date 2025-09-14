
'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import type { EodDataPoint } from '@/lib/types';
import { CartesianGrid, XAxis, YAxis, LineChart, Line } from 'recharts';
import { format, parseISO } from 'date-fns';

interface StockChartProps {
  data: EodDataPoint[];
  symbol: string;
}

const chartConfig = {
  price: {
    label: 'Price',
    color: 'hsl(var(--chart-2))',
  },
  sma: {
    label: 'SMA',
    color: 'hsl(var(--chart-1))',
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
          <LineChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={value => {
                if (typeof value !== 'string') return value;
                const date = parseISO(value);
                return format(date, 'MMM dd');
              }}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickCount={4}
              domain={['dataMin - 5', 'dataMax + 5']}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  indicator="line"
                  labelFormatter={(value, payload) => {
                    const datePoint = payload?.[0]?.payload;
                    if (datePoint) {
                        return format(parseISO(datePoint.date), 'MMM dd, yyyy');
                    }
                    return value;
                  }}
                />
              }
            />
            <Line
              dataKey="price"
              type="natural"
              stroke="var(--color-price)"
              strokeWidth={2}
              dot={false}
            />
            <Line
              dataKey="sma"
              type="natural"
              stroke="var(--color-sma)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}

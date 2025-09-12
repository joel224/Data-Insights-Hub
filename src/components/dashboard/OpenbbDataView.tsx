'use client';

import { Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart, XAxis, YAxis, Tooltip } from 'recharts';
import { Newspaper } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ChartContainer, ChartTooltipContent, type ChartConfig } from '@/components/ui/chart';
import type { OpenBBData } from '@/lib/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import Link from 'next/link';

interface OpenbbDataViewProps {
  data: OpenBBData;
}

const mainChartConfig = {
  close: {
    label: 'Price',
    color: 'hsl(var(--chart-1))',
  },
  sma: {
    label: 'SMA',
    color: 'hsl(var(--chart-2))',
  },
} satisfies ChartConfig;

const rsiChartConfig = {
    rsi: {
        label: 'RSI',
        color: 'hsl(var(--chart-3))',
    }
} satisfies ChartConfig

export function OpenbbDataView({ data }: OpenbbDataViewProps) {
  const { chartData, news, performance } = data;
  return (
    <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
      <div className='lg:col-span-2 space-y-6'>
        <Card>
          <CardHeader>
            <CardTitle>Stock Performance</CardTitle>
            <CardDescription>Price vs. Simple Moving Average (SMA)</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={mainChartConfig} className="h-[300px] w-full">
              <LineChart data={chartData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis tickLine={false} axisLine={false} tickMargin={8} domain={['dataMin - 10', 'dataMax + 10']} tickFormatter={value => `$${value}`} />
                <Tooltip content={<ChartTooltipContent indicator="dot" />} />
                <Line dataKey="close" type="monotone" stroke="var(--color-close)" strokeWidth={2} dot={false} name="Price" />
                <Line dataKey="sma" type="monotone" stroke="var(--color-sma)" strokeWidth={2} dot={false} name="SMA" />
              </LineChart>
            </ChartContainer>
          </CardContent>
        </Card>
        <Card>
            <CardHeader>
                <CardTitle>Relative Strength Index (RSI)</CardTitle>
                <CardDescription>Overbought (&gt;70) vs. Oversold (&lt;30)</CardDescription>
            </CardHeader>
            <CardContent>
                <ChartContainer config={rsiChartConfig} className='h-[150px] w-full'>
                    <BarChart data={chartData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="date" tickLine={false} axisLine={false} tickMargin={8} />
                        <YAxis dataKey="rsi" tickLine={false} axisLine={false} tickMargin={8} domain={[0, 100]} />
                        <Tooltip content={<ChartTooltipContent indicator="dot" />} />
                        <Bar dataKey="rsi" fill="var(--color-rsi)" radius={4} />
                    </BarChart>
                </ChartContainer>
            </CardContent>
        </Card>
      </div>
      <div className='space-y-6'>
        <Card>
            <CardHeader>
                <CardTitle>Performance</CardTitle>
            </CardHeader>
            <CardContent className='grid grid-cols-3 gap-4 text-center'>
                <div>
                    <p className='text-sm text-muted-foreground'>Volatility</p>
                    <p className='text-xl font-bold'>{performance.volatility}</p>
                </div>
                <div>
                    <p className='text-sm text-muted-foreground'>Sharpe Ratio</p>
                    <p className='text-xl font-bold'>{performance.sharpeRatio}</p>
                </div>
                <div>
                    <p className='text-sm text-muted-foreground'>Annual Return</p>
                    <p className='text-xl font-bold'>{performance.annualReturn}</p>
                </div>
            </CardContent>
        </Card>
        <Card>
            <CardHeader>
                <CardTitle className='flex items-center gap-2'><Newspaper size={20} /> Latest News</CardTitle>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableBody>
                        {news.map(item => (
                            <TableRow key={item.id}>
                                <TableCell>
                                    <Link href={item.url} target='_blank' className='hover:underline'>{item.title}</Link>
                                    <p className='text-xs text-muted-foreground'>{item.source} - {item.published}</p>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
      </div>
    </div>
  );
}

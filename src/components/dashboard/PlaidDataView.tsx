
'use client';

import { Newspaper } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import type { PlaidData, OpenBBNews } from '@/lib/types';
import { Table, TableBody, TableCell, TableRow } from '../ui/table';
import Link from 'next/link';
import { StockChart } from './StockChart';
import { RsiChart } from './RsiChart';

interface PlaidDataViewProps {
  data: PlaidData;
}

export function PlaidDataView({ data }: PlaidDataViewProps) {
  const { eod, news, symbol } = data;

  const performanceMetrics = [
    { label: 'Volatility', value: '15.2%' },
    { label: 'Sharpe Ratio', value: '1.8' },
    { label: 'Annual Return', value: '25.4%' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <StockChart data={eod} symbol={symbol} />
        <RsiChart data={eod} />
      </div>
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Performance</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-3 gap-4 text-center">
            {performanceMetrics.map(metric => (
              <div key={metric.label}>
                <p className="text-sm text-muted-foreground">{metric.label}</p>
                <p className="text-2xl font-bold">{metric.value}</p>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Newspaper size={20} /> Latest News
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableBody>
                {news && news.length > 0 ? (
                  news.map(item => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Link href={item.url} target="_blank" className="hover:underline font-medium">
                          {item.title}
                        </Link>
                        <p className="text-xs text-muted-foreground mt-1">
                          {item.source} - {item.published}
                        </p>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell className="text-center text-muted-foreground">
                      No news data available.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

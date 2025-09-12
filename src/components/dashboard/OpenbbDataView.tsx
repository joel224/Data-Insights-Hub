
'use client';

import { Newspaper } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import type { OpenBBData } from '@/lib/types';
import { Table, TableBody, TableCell, TableRow } from '../ui/table';
import Link from 'next/link';

interface OpenbbDataViewProps {
  data: OpenBBData;
}

export function OpenbbDataView({ data }: OpenbbDataViewProps) {
  const { news } = data;
  return (
    <div className='space-y-6'>
        <Card>
            <CardHeader>
                <CardTitle className='flex items-center gap-2'><Newspaper size={20} /> Latest Financial News</CardTitle>
                <CardDescription>
                  Real-time business and financial news headlines. The AI insights are generated based on this data.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableBody>
                        {news && news.length > 0 ? (
                            news.map(item => (
                                <TableRow key={item.id}>
                                    <TableCell>
                                        <Link href={item.url} target='_blank' className='hover:underline font-medium'>{item.title}</Link>
                                        <p className='text-xs text-muted-foreground mt-1'>{item.source} - {item.published}</p>
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell className="text-center text-muted-foreground">
                                    No news data available. Please ensure the scheduler has run and the NEWS_API_KEY is set.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
      </div>
  );
}


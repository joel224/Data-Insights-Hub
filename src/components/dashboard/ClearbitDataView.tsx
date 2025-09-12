
import { Newspaper } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import type { OpenBBNews } from '@/lib/types';
import { Table, TableBody, TableCell, TableRow } from '../ui/table';
import Link from 'next/link';

interface ClearbitDataViewProps {
  data: OpenBBNews[];
}

export function ClearbitDataView({ data }: ClearbitDataViewProps) {
  return (
    <Card>
      <CardHeader>
          <CardTitle className='flex items-center gap-2'><Newspaper size={20} /> General Business News</CardTitle>
          <CardDescription>
            Real-time business news headlines. The AI insights for Clearbit are generated based on this data.
          </CardDescription>
      </CardHeader>
      <CardContent>
          <Table>
              <TableBody>
                  {data && data.length > 0 ? (
                      data.map(item => (
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
                              No news data available. The scheduler may not have run yet.
                          </TableCell>
                      </TableRow>
                  )}
              </TableBody>
          </Table>
      </CardContent>
    </Card>
  );
}

    
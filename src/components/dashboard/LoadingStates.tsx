import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

export function InsightsSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-32" />
      </CardHeader>
      <CardContent className="space-y-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </CardContent>
    </Card>
  );
}

export function OpenbbDataSkeleton() {
    return (
        <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
            <div className='lg:col-span-2 space-y-6'>
                <Card>
                    <CardHeader>
                        <Skeleton className="h-6 w-48" />
                        <Skeleton className="h-4 w-64" />
                    </CardHeader>
                    <CardContent>
                        <Skeleton className="h-[300px] w-full" />
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <Skeleton className="h-6 w-48" />
                        <Skeleton className="h-4 w-64" />
                    </CardHeader>
                    <CardContent>
                        <Skeleton className="h-[150px] w-full" />
                    </CardContent>
                </Card>
            </div>
            <div className='space-y-6'>
                <Card>
                    <CardHeader>
                        <Skeleton className="h-6 w-32" />
                    </CardHeader>
                    <CardContent className='grid grid-cols-3 gap-4'>
                        <div className="space-y-2">
                            <Skeleton className="h-4 w-20 mx-auto" />
                            <Skeleton className="h-6 w-16 mx-auto" />
                        </div>
                        <div className="space-y-2">
                            <Skeleton className="h-4 w-20 mx-auto" />
                            <Skeleton className="h-6 w-12 mx-auto" />
                        </div>
                        <div className="space-y-2">
                            <Skeleton className="h-4 w-24 mx-auto" />
                            <Skeleton className="h-6 w-16 mx-auto" />
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <Skeleton className="h-6 w-40" />
                    </CardHeader>
                    <CardContent className='space-y-4'>
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className='space-y-1'>
                                <Skeleton className="h-4 w-full" />
                                <Skeleton className="h-3 w-32" />
                            </div>
                        ))}
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}

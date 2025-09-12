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

export function PlaidDataSkeleton() {
    return (
        <Card>
            <CardHeader>
                <Skeleton className="h-6 w-48" />
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead><Skeleton className="h-5 w-24" /></TableHead>
                            <TableHead><Skeleton className="h-5 w-32" /></TableHead>
                            <TableHead><Skeleton className="h-5 w-20" /></TableHead>
                            <TableHead className="text-right"><Skeleton className="h-5 w-24 ml-auto" /></TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {[...Array(5)].map((_, i) => (
                            <TableRow key={i}>
                                <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                <TableCell><Skeleton className="h-4 w-36" /></TableCell>
                                <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                <TableCell className="text-right"><Skeleton className="h-4 w-20 ml-auto" /></TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}

export function ClearbitDataSkeleton() {
    return (
        <div className="space-y-6">
            <Card>
                <CardHeader className="flex flex-row items-start gap-4 space-y-0">
                    <Skeleton className="h-16 w-16 rounded-lg" />
                    <div className="flex-1 space-y-2">
                        <Skeleton className="h-8 w-48" />
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-4 w-24" />
                    </div>
                </CardHeader>
                <CardContent>
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-4/5 mt-2" />
                </CardContent>
            </Card>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
                {[...Array(4)].map((_, i) => (
                    <Card key={i}>
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <Skeleton className="h-5 w-24" />
                            <Skeleton className="h-6 w-6 rounded-full" />
                        </CardHeader>
                        <CardContent>
                            <Skeleton className="h-8 w-20" />
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    )
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

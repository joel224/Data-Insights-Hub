
'use client';

import { Logo } from '@/components/icons/Logo';
import { Skeleton } from '@/components/ui/skeleton';
import dynamic from 'next/dynamic';

const Dashboard = dynamic(() => import('@/components/dashboard/Dashboard').then(mod => mod.Dashboard), {
  ssr: false,
  loading: () => (
    <div className="space-y-4">
      <Skeleton className="h-10 w-[300px]" />
      <div className="flex flex-1 items-center justify-center rounded-lg border border-dashed shadow-sm p-8">
        <div className="flex flex-col items-center gap-2 text-center">
            <h3 className="text-2xl font-bold tracking-tight">
                Loading Dashboard...
            </h3>
            <p className="text-sm text-muted-foreground">
                Please wait while the data is being prepared.
            </p>
        </div>
      </div>
    </div>
  ),
});

export default function Home() {
  return (
    <div className="flex min-h-screen w-full flex-col bg-background">
      <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60 md:px-6">
        <div className="flex items-center gap-2">
          <Logo />
          <h1 className="font-headline text-xl font-semibold text-foreground">
            Data Insights Hub
          </h1>
        </div>
      </header>
      <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
        <Dashboard />
      </main>
    </div>
  );
}

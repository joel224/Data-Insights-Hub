'use client';

import { useState, useTransition } from 'react';
import { Building2, Landmark, LineChart, Loader2 } from 'lucide-react';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { runPipeline } from '@/app/actions';
import type { ClearbitData, DataSource, OpenBBStockData, PlaidTransaction, PipelineState } from '@/lib/types';

import { PlaidDataView } from './PlaidDataView';
import { ClearbitDataView } from './ClearbitDataView';
import { OpenbbDataView } from './OpenbbDataView';
import { InsightsCard } from './InsightsCard';
import { InsightsSkeleton, PlaidDataSkeleton, ClearbitDataSkeleton, OpenbbDataSkeleton } from './LoadingStates';

export function Dashboard() {
  const [isPending, startTransition] = useTransition();
  const { toast } = useToast();

  const [activeDataSource, setActiveDataSource] = useState<DataSource | null>(null);

  const [plaidState, setPlaidState] = useState<PipelineState<PlaidTransaction[]>>({ data: null, insights: null });
  const [clearbitState, setClearbitState] = useState<PipelineState<ClearbitData>>({ data: null, insights: null });
  const [openbbState, setOpenbbState] = useState<PipelineState<OpenBBStockData[]>>({ data: null, insights: null });

  const handleGenerate = (dataSource: DataSource) => {
    setActiveDataSource(dataSource);
    startTransition(async () => {
      const result = await runPipeline(dataSource);

      if (result.error) {
        toast({
          variant: 'destructive',
          title: 'An error occurred',
          description: result.error,
        });
        setActiveDataSource(null);
        return;
      }
      
      switch (dataSource) {
        case 'plaid':
          setPlaidState({ data: result.data, insights: result.insights ?? null });
          break;
        case 'clearbit':
          setClearbitState({ data: result.data, insights: result.insights ?? null });
          break;
        case 'openbb':
          setOpenbbState({ data: result.data, insights: result.insights ?? null });
          break;
      }
      setActiveDataSource(null);
    });
  };

  const isLoading = (dataSource: DataSource) => isPending && activeDataSource === dataSource;

  const renderInitialState = (dataSource: DataSource, title: string) => (
    <div className="flex flex-1 items-center justify-center rounded-lg border border-dashed shadow-sm">
        <div className="flex flex-col items-center gap-2 text-center">
            <h3 className="text-2xl font-bold tracking-tight">
                No {title} Data
            </h3>
            <p className="text-sm text-muted-foreground">
                Click the button below to fetch data and generate insights.
            </p>
            <Button className="mt-4" onClick={() => handleGenerate(dataSource)} disabled={isPending}>
                {isLoading(dataSource) ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Generate Insights
            </Button>
        </div>
    </div>
  )

  return (
    <Tabs defaultValue="plaid" className="space-y-4">
      <TabsList>
        <TabsTrigger value="plaid"><Landmark className="mr-2 h-4 w-4" />Plaid</TabsTrigger>
        <TabsTrigger value="clearbit"><Building2 className="mr-2 h-4 w-4" />Clearbit</TabsTrigger>
        <TabsTrigger value="openbb"><LineChart className="mr-2 h-4 w-4" />OpenBB</TabsTrigger>
      </TabsList>
      
      <TabsContent value="plaid" className="space-y-4">
        {plaidState.data ? (
            <div className="space-y-6">
                <PlaidDataView data={plaidState.data} />
                {plaidState.insights && <InsightsCard insights={plaidState.insights} />}
            </div>
        ) : isLoading('plaid') ? (
            <div className="space-y-6">
                <PlaidDataSkeleton />
                <InsightsSkeleton />
            </div>
        ) : (
            renderInitialState('plaid', 'Financial')
        )}
      </TabsContent>

      <TabsContent value="clearbit" className="space-y-4">
        {clearbitState.data ? (
            <div className="space-y-6">
                <ClearbitDataView data={clearbitState.data} />
                {clearbitState.insights && <InsightsCard insights={clearbitState.insights} />}
            </div>
        ) : isLoading('clearbit') ? (
            <div className="space-y-6">
                <ClearbitDataSkeleton />
                <InsightsSkeleton />
            </div>
        ) : (
            renderInitialState('clearbit', 'Company')
        )}
      </TabsContent>

      <TabsContent value="openbb" className="space-y-4">
        {openbbState.data ? (
            <div className="space-y-6">
                <OpenbbDataView data={openbbState.data} />
                {openbbState.insights && <InsightsCard insights={openbbState.insights} />}
            </div>
        ) : isLoading('openbb') ? (
            <div className="space-y-6">
                <OpenbbDataSkeleton />
                <InsightsSkeleton />
            </div>
        ) : (
            renderInitialState('openbb', 'Market')
        )}
      </TabsContent>
    </Tabs>
  );
}

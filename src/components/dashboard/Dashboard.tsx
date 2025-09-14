
'use client';

import { useState, useTransition, useEffect } from 'react';
import { Building2, Landmark, LineChart, Loader2 } from 'lucide-react';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import type { ClearbitData, DataSource, OpenBBData, PipelineState, PlaidData } from '@/lib/types';

import { PlaidDataView } from './PlaidDataView';
import { ClearbitDataView } from './ClearbitDataView';
import { OpenbbDataView } from './OpenbbDataView';
import { InsightsCard } from './InsightsCard';
import { InsightsSkeleton, OpenbbDataSkeleton } from './LoadingStates';

async function fetchPipelineData(dataSource: DataSource): Promise<{ data: any; insights?: string; error?: string }> {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const response = await fetch(`${baseUrl}/api/get-latest-data/${dataSource}`, { cache: 'no-store' });
    if (!response.ok) {
      const errorText = await response.text();
      try {
        const errorJson = JSON.parse(errorText);
        throw new Error(`Failed to fetch data for ${dataSource}: ${errorJson.detail || errorText}`);
      } catch (e) {
        throw new Error(`Failed to fetch data for ${dataSource}: ${errorText}`);
      }
    }
    const result = await response.json();
    return { data: result.data, insights: result.insights };

  } catch (e) {
    console.error(`Pipeline failed for ${dataSource}:`, e);
    const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred.';
    return {
      data: null,
      error: `Failed to process data. Please ensure the Python backend is running and data has been fetched by the scheduler. Details: ${errorMessage}`,
    };
  }
}


export function Dashboard() {
  const [isPending, startTransition] = useTransition();
  const { toast } = useToast();

  const [activeDataSource, setActiveDataSource] = useState<DataSource | null>('plaid');

  const [plaidState, setPlaidState] = useState<PipelineState<PlaidData>>({ data: null, insights: null });
  const [clearbitState, setClearbitState] = useState<PipelineState<ClearbitData>>({ data: null, insights: null });
  const [openbbState, setOpenbbState] = useState<PipelineState<OpenBBData>>({ data: null, insights: null });
  
  useEffect(() => {
    handleGenerate('plaid');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGenerate = (dataSource: DataSource) => {
    setActiveDataSource(dataSource);
    startTransition(async () => {
      const result = await fetchPipelineData(dataSource);

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

  const getButtonText = (dataSource: DataSource) => {
      switch (dataSource) {
          case 'plaid':
              return plaidState.data ? 'Refresh Insights' : 'Load Insights';
          case 'clearbit':
              return clearbitState.data ? 'Refresh Insights' : 'Load Insights';
          case 'openbb':
              return openbbState.data ? 'Refresh Insights' : 'Load Insights';
      }
  }
  
  const handleTabChange = (value: string) => {
    const dataSource = value as DataSource;
    switch (dataSource) {
      case 'plaid':
        if (!plaidState.data) handleGenerate('plaid');
        break;
      case 'clearbit':
        if (!clearbitState.data) handleGenerate('clearbit');
        break;
      case 'openbb':
        if (!openbbState.data) handleGenerate('openbb');
        break;
    }
  }

  const renderInitialState = (dataSource: DataSource, title: string) => (
    <div className="flex flex-1 items-center justify-center rounded-lg border border-dashed shadow-sm">
        <div className="flex flex-col items-center gap-2 text-center">
            <h3 className="text-2xl font-bold tracking-tight">
                No {title} Data Loaded
            </h3>
            <p className="text-sm text-muted-foreground">
                Click the button below to load data and insights from the latest daily pipeline.
            </p>
            <Button className="mt-4" onClick={() => handleGenerate(dataSource)} disabled={isPending}>
                {isLoading(dataSource) ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                {getButtonText(dataSource)}
            </Button>
        </div>
    </div>
  )

  return (
    <Tabs defaultValue="plaid" className="space-y-4" onValueChange={handleTabChange}>
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
                <OpenbbDataSkeleton />
                <InsightsSkeleton />
            </div>
        ) : (
            renderInitialState('plaid', 'Financial')
        )}
      </TabsContent>

      <TabsContent value="clearbit" className="space-y-4">
        {clearbitState.data ? (
            <div className="space-y-6">
                <ClearbitDataView data={clearbitState.data.news || []} />
                {clearbitState.insights && <InsightsCard insights={clearbitState.insights} />}
            </div>
        ) : isLoading('clearbit') ? (
            <div className="space-y-6">
                <OpenbbDataSkeleton />
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

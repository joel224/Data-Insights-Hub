'use client';

import { useState, useTransition } from 'react';
import { Building2, Landmark, LineChart, Loader2 } from 'lucide-react';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import type { ClearbitData, DataSource, OpenBBData, PlaidTransaction, PipelineState } from '@/lib/types';

import { PlaidDataView } from './PlaidDataView';
import { ClearbitDataView } from './ClearbitDataView';
import { OpenbbDataView } from './OpenbbDataView';
import { InsightsCard } from './InsightsCard';
import { InsightsSkeleton, PlaidDataSkeleton, ClearbitDataSkeleton, OpenbbDataSkeleton } from './LoadingStates';

// In a real deployment, this would be an absolute URL to the deployed backend.
// For the single-container setup, we use a relative path.
const API_BASE_URL = '/api';

async function runPipeline(dataSource: DataSource): Promise<{ data: any; insights?: string; error?: string }> {
  try {
    // 1. Fetch the latest data from the Python backend's existing endpoint
    const dataResponse = await fetch(`${API_BASE_URL}/get-latest-data/${dataSource}`, { cache: 'no-store' });
    if (!dataResponse.ok) {
      const errorText = await dataResponse.text();
      throw new Error(`Failed to fetch data for ${dataSource}: ${errorText}`);
    }
    const data = await dataResponse.json();

    // 2. Generate insights by calling the new Python endpoint
    const insightsResponse = await fetch(`${API_BASE_URL}/generate-insights`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        dataSource,
        data: JSON.stringify(data, null, 2),
      }),
    });

    if (!insightsResponse.ok) {
      const errorText = await insightsResponse.text();
      throw new Error(`Failed to generate insights for ${dataSource}: ${errorText}`);
    }
    const insightsResult = await insightsResponse.json();

    return { data, insights: insightsResult.insights };
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

  const [activeDataSource, setActiveDataSource] = useState<DataSource | null>(null);

  const [plaidState, setPlaidState] = useState<PipelineState<PlaidTransaction[]>>({ data: null, insights: null });
  const [clearbitState, setClearbitState] = useState<PipelineState<ClearbitData>>({ data: null, insights: null });
  const [openbbState, setOpenbbState] = useState<PipelineState<OpenBBData>>({ data: null, insights: null });

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

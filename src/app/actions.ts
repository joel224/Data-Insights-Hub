'use server';

import { generateDataInsights } from '@/ai/flows/generate-data-insights';
import { fetchClearbitData } from '@/lib/data/clearbit';
import { fetchOpenbbData } from '@/lib/data/openbb';
import { fetchPlaidData } from '@/lib/data/plaid';
import type { DataSource } from '@/lib/types';

export async function runPipeline(dataSource: DataSource): Promise<{ data: any; insights?: string; error?: string }> {
  try {
    let data;

    switch (dataSource) {
      case 'plaid':
        data = await fetchPlaidData();
        break;
      case 'clearbit':
        data = await fetchClearbitData();
        break;
      case 'openbb':
        data = await fetchOpenbbData();
        break;
      default:
        // This case should not be reachable with TypeScript, but it's good practice
        throw new Error('Invalid data source');
    }

    const insightsResult = await generateDataInsights({
      dataSource,
      data: JSON.stringify(data, null, 2),
    });

    return { data, insights: insightsResult.insights };
  } catch (e) {
    console.error(`Pipeline failed for ${dataSource}:`, e);
    return { data: null, error: e instanceof Error ? e.message : 'An unknown error occurred while generating insights.' };
  }
}

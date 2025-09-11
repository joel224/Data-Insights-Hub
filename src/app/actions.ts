'use server';

import { generateDataInsights } from '@/ai/flows/generate-data-insights';
import type { DataSource } from '@/lib/types';

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://127.0.0.1:8000';

async function fetchDataFromPython(dataSource: DataSource) {
  const response = await fetch(`${PYTHON_BACKEND_URL}/api/data/${dataSource}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store', // Ensure fresh data is fetched every time
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch data from ${dataSource}: ${response.status} ${errorText}`);
  }
  return response.json();
}

export async function runPipeline(dataSource: DataSource): Promise<{ data: any; insights?: string; error?: string }> {
  try {
    const data = await fetchDataFromPython(dataSource);

    // The data storage in PostgreSQL should be handled by your Python backend
    // after fetching from the respective APIs.

    const insightsResult = await generateDataInsights({
      dataSource,
      data: JSON.stringify(data, null, 2),
    });

    return { data, insights: insightsResult.insights };
  } catch (e) {
    console.error(`Pipeline failed for ${dataSource}:`, e);
    const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred.';
    return { 
      data: null, 
      error: `Failed to connect to the Python backend. Please ensure it's running. Details: ${errorMessage}` 
    };
  }
}

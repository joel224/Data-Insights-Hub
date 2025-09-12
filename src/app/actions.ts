'use server';

import { generateDataInsights } from '@/ai/flows/generate-data-insights';
import type { DataSource } from '@/lib/types';

// In a real deployment, this would point to your Railway URL or other deployed backend.
// For local dev, it points to the local Python server.
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://127.0.0.1:8000';

async function fetchLatestDataFromPython(dataSource: DataSource) {
  // We add /api to the path to match the updated backend route
  const response = await fetch(`${PYTHON_BACKEND_URL}/api/get-latest-data/${dataSource}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store', // Ensure fresh data is fetched every time
  });

  if (!response.ok) {
    const errorText = await response.text();
    try {
      const errorJson = JSON.parse(errorText);
      throw new Error(`Failed to fetch latest data for ${dataSource}: ${errorJson.detail || errorText}`);
    } catch {
      throw new Error(`Failed to fetch latest data for ${dataSource}: ${response.status} ${errorText}`);
    }
  }
  return response.json();
}

export async function runPipeline(dataSource: DataSource): Promise<{ data: any; insights?: string; error?: string }> {
  try {
    // 1. Fetch the latest data that was stored by the scheduled job.
    const data = await fetchLatestDataFromPython(dataSource);

    // 2. Generate insights based on that data.
    const insightsResult = await generateDataInsights({
      dataSource,
      data: JSON.stringify(data, null, 2),
    });

    return { data, insights: insightsResult.insights };
  } catch (e) {
    console.error(`Pipeline failed for ${dataSource}:`, e);
    const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred.';
    // Updated error message for clarity
    return { 
      data: null, 
      error: `Failed to process data. Please ensure the Python backend is running and data has been fetched by the scheduler. Details: ${errorMessage}` 
    };
  }
}

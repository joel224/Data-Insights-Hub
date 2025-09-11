// This file is no longer used for data fetching.
// The data is now fetched from the Python backend.
// See /src/app/actions.ts

import type { ClearbitData } from '@/lib/types';

export async function fetchClearbitData(): Promise<ClearbitData> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  return {
    companyName: 'Innovate Inc.',
    domain: 'innovateinc.com',
    description: 'Innovate Inc. is a leading provider of cutting-edge technology solutions, specializing in AI-driven analytics and cloud computing services.',
    logo: 'https://picsum.photos/seed/innovate/100/100',
    location: 'San Francisco, CA',
    metrics: {
      employees: 1200,
      marketCap: '$15B',
      annualRevenue: '$2.5B',
      raised: '$500M',
    },
  };
}

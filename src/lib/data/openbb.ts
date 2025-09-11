import type { OpenBBStockData } from '@/lib/types';
import { subDays, format } from 'date-fns';

export async function fetchOpenbbData(): Promise<OpenBBStockData[]> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  const data: OpenBBStockData[] = [];
  const today = new Date();
  let currentPrice = 150;

  for (let i = 30; i >= 0; i--) {
    const date = subDays(today, i);
    currentPrice += (Math.random() - 0.5) * 5; // Fluctuate price
    currentPrice = Math.max(140, Math.min(160, currentPrice)); // Keep price within a range
    
    data.push({
      date: format(date, 'MMM d'),
      close: parseFloat(currentPrice.toFixed(2)),
    });
  }

  return data;
}

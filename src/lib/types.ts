export type PlaidTransaction = {
  id: string;
  date: string;
  name: string;
  amount: number;
  category: string;
};

export type ClearbitData = {
  companyName: string;
  domain: string;
  description: string;
  logo: string;
  location: string;
  metrics: {
    employees: number;
    marketCap: string;
    annualRevenue: string;
    raised: string;
  };
};

export type OpenBBStockData = {
  date: string;
  close: number;
  sma: number; // Simple Moving Average
  rsi: number; // Relative Strength Index
};

export type OpenBBNews = {
  id: string;
  title: string;
  url: string;
  source: string;
  published: string;
}

export type OpenBBData = {
  chartData: OpenBBStockData[];
  news: OpenBBNews[];
  performance: {
    volatility: string;
    sharpeRatio: string;
    annualReturn: string;
  }
}

export type DataSource = 'plaid' | 'clearbit' | 'openbb';

export type PipelineState<T> = {
  data: T | null;
  insights: string | null;
  error?: string | null;
};



export type EodDataPoint = {
  date: string;
  price: number;
  sma: number;
  rsi: number;
}

export type PlaidData = {
  eod: EodDataPoint[];
  symbol: string;
  news?: OpenBBNews[];
}

export type PlaidTransaction = {
  id: string;
  date: string;
  name: string;
  amount: number;
  category: string;
};

export type ClearbitData = {
  companyName?: string;
  domain?: string;
  description?: string;
  logo?: string;
  location?: string;
  metrics?: {
    employees: number;
    marketCap: string;
    annualRevenue: string;
    raised: string;
  };
  news?: OpenBBNews[];
};

export type OpenBBNews = {
  id: string;
  title: string;
  url: string;
  source: string;
  published: string;
}

export type OpenBBData = {
  news: OpenBBNews[];
}

export type DataSource = 'plaid' | 'clearbit' | 'openbb';

export type PipelineState<T> = {
  data: T | null;
  insights: string | null;
  error?: string | null;
};

    

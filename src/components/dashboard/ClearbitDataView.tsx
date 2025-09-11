import Image from 'next/image';
import { Building, DollarSign, Globe, TrendingUp, Users } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { ClearbitData } from '@/lib/types';

interface ClearbitDataViewProps {
  data: ClearbitData;
}

export function ClearbitDataView({ data }: ClearbitDataViewProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-start gap-4 space-y-0">
          <Image
            src={data.logo}
            alt={`${data.companyName} logo`}
            width={64}
            height={64}
            className="rounded-lg border"
            data-ai-hint="company logo"
          />
          <div className="flex-1">
            <CardTitle className="font-headline text-3xl">{data.companyName}</CardTitle>
            <CardDescription className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              {data.domain}
            </CardDescription>
            <CardDescription className="mt-1 flex items-center gap-2">
              <Building className="h-4 w-4" />
              {data.location}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{data.description}</p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Employees</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.metrics.employees.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Market Cap</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.metrics.marketCap}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Annual Revenue</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.metrics.annualRevenue}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Raised</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.metrics.raised}</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

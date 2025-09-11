import { Lightbulb } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface InsightsCardProps {
  insights: string;
}

export function InsightsCard({ insights }: InsightsCardProps) {
  return (
    <Card className="bg-accent/40 border-accent">
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <Lightbulb className="h-5 w-5 text-accent-foreground" />
        <CardTitle className="text-accent-foreground">AI Insights</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="prose prose-sm max-w-none text-accent-foreground">
          {insights.split('\n').map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

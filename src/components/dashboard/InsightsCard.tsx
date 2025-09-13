import { Lightbulb } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface InsightsCardProps {
  insights: string;
}

// Function to parse the simple markdown-like format
const formatInsights = (text: string) => {
  // Replace **text** with <strong>text</strong>
  let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Split by newlines to handle paragraphs and lists
  const lines = html.split('\n').filter(line => line.trim() !== '');

  let inList = false;
  const formattedLines = lines.map(line => {
    // Match lines starting with a number and a period (e.g., "1.")
    if (/^\d+\./.test(line.trim())) {
      const listItem = `<li>${line.trim().substring(line.trim().indexOf(' ') + 1)}</li>`;
      if (!inList) {
        inList = true;
        return `<ol className="list-decimal pl-5 space-y-2 mt-2">${listItem}`;
      }
      return listItem;
    } else {
      const closingTag = inList ? '</ol>' : '';
      inList = false;
      return `${closingTag}<p>${line}</p>`;
    }
  });

  if (inList) {
    formattedLines.push('</ol>');
  }

  return formattedLines.join('');
};

export function InsightsCard({ insights }: InsightsCardProps) {
  const formattedInsights = formatInsights(insights);

  return (
    <Card className="bg-accent/40 border-accent">
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <Lightbulb className="h-5 w-5 text-accent-foreground" />
        <CardTitle className="text-accent-foreground">AI Insights</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className="prose prose-sm max-w-none text-accent-foreground prose-strong:text-accent-foreground prose-p:my-2 prose-ol:my-2"
          dangerouslySetInnerHTML={{ __html: formattedInsights }}
        />
      </CardContent>
    </Card>
  );
}

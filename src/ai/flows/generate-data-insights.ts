'use server';

/**
 * @fileOverview Generates insights from fetched data using an LLM, with data-source-specific prompts.
 *
 * - generateDataInsights - A function that handles the generation of insights.
 * - GenerateDataInsightsInput - The input type for the generateDataInsights function.
 * - GenerateDataInsightsOutput - The return type for the generateDataInsights function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateDataInsightsInputSchema = z.object({
  dataSource: z.enum(['plaid', 'clearbit', 'openbb']).describe('The data source to generate insights from.'),
  data: z.string().describe('The data to generate insights from. Should be stringified JSON.'),
});
export type GenerateDataInsightsInput = z.infer<typeof GenerateDataInsightsInputSchema>;

const GenerateDataInsightsOutputSchema = z.object({
  insights: z.string().describe('The generated insights from the data.'),
});
export type GenerateDataInsightsOutput = z.infer<typeof GenerateDataInsightsOutputSchema>;

export async function generateDataInsights(input: GenerateDataInsightsInput): Promise<GenerateDataInsightsOutput> {
  return generateDataInsightsFlow(input);
}

const plaidPrompt = `You are a fintech analyst. Based on the following financial transaction data, provide a short summary and 3 actionable recommendations to improve financial performance.

Data:
{{{data}}}`;

const clearbitPrompt = `You are a fintech analyst. Based on the following company performance data, provide a short summary and 3 actionable recommendations to improve business performance and market position.

Data:
{{{data}}}`;

const openbbPrompt = `You are a fintech analyst. Based on the following stock market performance data (including chart data, news, and performance metrics), provide a short summary and 3 actionable recommendations for a potential investor.

Data:
{{{data}}}`;


const generateDataInsightsFlow = ai.defineFlow(
  {
    name: 'generateDataInsightsFlow',
    inputSchema: GenerateDataInsightsInputSchema,
    outputSchema: GenerateDataInsightsOutputSchema,
  },
  async (input) => {
    let promptText = '';
    switch (input.dataSource) {
      case 'plaid':
        promptText = plaidPrompt;
        break;
      case 'clearbit':
        promptText = clearbitPrompt;
        break;
      case 'openbb':
        promptText = openbbPrompt;
        break;
    }

    const prompt = ai.definePrompt({
      name: `generateDataInsightsPrompt-${input.dataSource}`,
      prompt: promptText,
      input: { schema: GenerateDataInsightsInputSchema },
      output: { schema: GenerateDataInsightsOutputSchema },
    });

    const { output } = await prompt(input);
    return output!;
  }
);

# **App Name**: Data Insights Hub

## Core Features:

- Plaid Data Fetch: Fetch financial data using the Plaid API (mock for MVP).
- Clearbit Data Fetch: Fetch website traffic and customer info using the Clearbit API (mock for MVP).
- OpenBB Data Fetch: Fetch market and stock data using the OpenBB API (mock for MVP).
- Data Storage: Store fetched data from Plaid, Clearbit, and OpenBB in separate PostgreSQL tables via the Railway hosted PostgreSQL instance.
- LLM Insights Generation: Generate insights based on the fetched data using an LLM tool, with data-source-specific prompts.
- Dashboard UI: Display data and insights in a single-page React dashboard with tabs for Plaid, Clearbit, and OpenBB data.
- Data Pipeline Trigger: Allow users to trigger data fetching and processing for each data source via a single API endpoint.

## Style Guidelines:

- Primary color: Teal blue (#4DB6AC), evoking stability and trustworthiness suitable for financial data.
- Background color: Light grey (#F0F4F3), a clean and neutral backdrop that complements the primary color without distracting from the data.
- Accent color: Soft yellow (#E6EE9C) for interactive elements and highlights, offering a gentle contrast to the primary color to draw user attention.
- Body and headline font: 'Inter', a grotesque-style sans-serif, offering a modern, objective look, for headlines or body text
- Use clear, minimalist icons to represent different data categories and actions.
- Employ a clean and structured layout with clear separation between sections for each data source.
- Use subtle animations to indicate data loading and processing states.
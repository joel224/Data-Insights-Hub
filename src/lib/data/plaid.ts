import type { PlaidTransaction } from '@/lib/types';

export async function fetchPlaidData(): Promise<PlaidTransaction[]> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  return [
    { id: '1', date: '2024-07-20', name: 'Coffee Shop', amount: -5.75, category: 'Food and Drink' },
    { id: '2', date: '2024-07-20', name: 'Online Subscription', amount: -14.99, category: 'Services' },
    { id: '3', date: '2024-07-19', name: 'Grocery Store', amount: -85.4, category: 'Groceries' },
    { id: '4', date: '2024-07-18', name: 'Salary Deposit', amount: 2500, category: 'Income' },
    { id: '5', date: '2024-07-18', name: 'Gas Station', amount: -45.22, category: 'Travel' },
    { id: '6', date: '2024-07-17', name: 'Bookstore', amount: -25.0, category: 'Shopping' },
    { id: '7', date: '2024-07-16', name: 'Restaurant', amount: -62.11, category: 'Food and Drink' },
    { id: '8', date: '2024-07-15', name: 'Utility Bill', amount: -120.0, category: 'Bills' },
  ];
}

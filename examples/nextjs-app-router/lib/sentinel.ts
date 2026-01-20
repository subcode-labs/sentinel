import { SentinelClient } from '../../../sdks/typescript/src';

// Initialize the Sentinel Client
// In a real Next.js app, you would install via: npm install @subcode/sentinel-client
export const sentinel = new SentinelClient({
  // Load from environment variables (e.g. .env.local)
  baseUrl: process.env.SENTINEL_URL || 'http://localhost:3000',
  apiToken: process.env.SENTINEL_TOKEN,
  agentId: 'nextjs-app', // Identify this application
});

import app from './src/server';

const port = parseInt(process.env.PORT || "3000");

console.log(`Sentinel Vault (Prototype) running on port ${port}`);
console.log(`Master Token: sentinel_dev_key`);

export default {
  port,
  fetch: app.fetch,
};

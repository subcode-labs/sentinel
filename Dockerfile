# Use the official Bun image
FROM oven/bun:1 AS base
WORKDIR /app

# Install dependencies
# Copy package files
COPY package.json bun.lock ./
# Install production dependencies
RUN bun install --frozen-lockfile --production

# Copy source code
COPY src ./src
COPY tsconfig.json ./
# Copy other necessary files if any (e.g. migrations)

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0
ENV DB_PATH=/app/data/sentinel.db

# Expose port
EXPOSE 3000

# Create data directory
RUN mkdir -p /app/data

# Start the server
CMD ["bun", "src/server.ts"]

FROM node:22-alpine

WORKDIR /app
COPY apps/frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY apps/frontend/ ./

# The frontend proxies /api/* to the private backend over the Docker network.
ENV CAREERPILOT_API_INTERNAL_URL=http://backend:8000
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000
CMD ["npm", "run", "start", "--", "-H", "0.0.0.0", "-p", "3000"]

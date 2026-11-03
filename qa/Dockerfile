FROM mcr.microsoft.com/playwright:v1.56.1-noble
WORKDIR /qa
ENV CI=1
COPY package.json package-lock.json ./
RUN npm ci
COPY playwright.config.ts tsconfig.json eslint.config.js cucumber.mjs ./
COPY automation ./automation
CMD ["npx", "playwright", "test", "--grep", "@smoke"]

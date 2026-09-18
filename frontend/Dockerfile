# Build multi-stage: a imagem final não carrega Node nem node_modules,
# só os arquivos estáticos já compilados + um nginx enxuto para servi-los.

FROM node:20-alpine AS build
WORKDIR /app

# VITE_API_URL precisa existir NO MOMENTO DO BUILD, não em runtime: o
# Vite substitui `import.meta.env.VITE_API_URL` pelo valor literal
# dentro do JS gerado (não é uma variável de ambiente lida pelo
# navegador depois). Por isso vem como build arg do docker-compose,
# não como `environment:` do serviço.
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

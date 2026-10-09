import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import path from "path";

// Configuração do Vite: React + PWA instalável.
// O PWA usa estratégia "prompt" (não força atualização silenciosa) e
// cacheia o app shell para permitir abrir o app offline — os dados em
// si (check-ins feitos offline) são sincronizados pela camada de
// serviços do frontend (ver src/services/syncQueue.ts, Etapa 12).
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "prompt",
      includeAssets: [
        "icons/icon-192.png",
        "icons/icon-512.png",
        "icons/maskable-icon-192.png",
        "icons/maskable-icon-512.png",
      ],
      manifest: {
        name: "BodyTrack — Diário de Transformação",
        short_name: "BodyTrack",
        description: "Acompanhamento de recomposição corporal, treino e evolução física.",
        theme_color: "#0B0F19",
        background_color: "#0B0F19",
        display: "standalone",
        start_url: "/",
        icons: [
          // purpose "any" (padrão): usado como veio, sem recorte — é o
          // que aparece no iOS, no Windows e em launchers Android que
          // não aplicam máscara.
          { src: "icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
          // purpose "maskable": fundo sólido ocupando o quadrado
          // inteiro e a arte encolhida pra caber na "safe zone" — sem
          // isso, o Android recorta o ícone "any" (que já tem cantos
          // arredondados e fundo transparente) com a própria máscara
          // adaptativa e sobra um preenchimento branco em volta.
          { src: "icons/maskable-icon-192.png", sizes: "192x192", type: "image/png", purpose: "maskable" },
          { src: "icons/maskable-icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // As ~170 imagens de exercícios (3,5 MB) NÃO entram no pré-cache (baixaria
        // tudo na instalação do app). Em vez disso, cada imagem é guardada na
        // primeira vez que é vista e passa a funcionar offline (CacheFirst).
        globPatterns: ["**/*.{js,css,html,ico,png,svg}"],
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith("/exercises/"),
            handler: "CacheFirst",
            options: {
              cacheName: "exercise-images",
              expiration: { maxEntries: 300, maxAgeSeconds: 60 * 60 * 24 * 90 },
              cacheableResponse: { statuses: [200] },
            },
          },
          {
            // Vídeos próprios: o <video> pede o arquivo em pedaços (Range); sem
            // rangeRequests o cache offline não consegue responder a esses pedidos.
            urlPattern: ({ url }) => url.pathname.startsWith("/exercise-videos/"),
            handler: "CacheFirst",
            options: {
              cacheName: "exercise-videos",
              expiration: { maxEntries: 120, maxAgeSeconds: 60 * 60 * 24 * 90 },
              cacheableResponse: { statuses: [200] },
              rangeRequests: true,
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
  },
});

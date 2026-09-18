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
        globPatterns: ["**/*.{js,css,html,ico,png,svg}"],
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

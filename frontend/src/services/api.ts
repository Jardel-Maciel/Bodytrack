import axios from "axios";

/**
 * Cliente HTTP único da aplicação. Todo módulo de serviço (checkins,
 * workouts, measurements...) importa este `api` em vez de criar sua
 * própria instância — assim o token JWT e o tratamento de erro 401
 * (logout automático) ficam centralizados em um só lugar.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
});

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem("bodytrack.auth");
  if (raw) {
    const { token } = JSON.parse(raw);
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("bodytrack.auth");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

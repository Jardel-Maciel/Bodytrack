import { api } from "./api";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  birth_date: string | null;
  height_cm: number | null;
}

export interface ProfileUpdateInput {
  name?: string;
  birth_date?: string | null;
  height_cm?: number | null;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function login(email: string, password: string) {
  const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
  return data;
}

export async function register(input: { email: string; password: string; name: string }) {
  const { data } = await api.post<AuthUser>("/auth/register", input);
  return data;
}

export async function me() {
  const { data } = await api.get<AuthUser>("/auth/me");
  return data;
}

export async function updateMe(input: ProfileUpdateInput) {
  const { data } = await api.patch<AuthUser>("/auth/me", input);
  return data;
}

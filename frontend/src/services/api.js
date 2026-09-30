import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
  headers: { 'Content-Type': 'application/json' },
});

const PUBLIC_ENDPOINTS = ['/auth/login/', '/auth/register/', '/auth/refresh/'];

api.interceptors.request.use((config) => {
  const isPublic = PUBLIC_ENDPOINTS.some((path) => config.url?.endsWith(path));
  const token = localStorage.getItem('access');
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  if (token && !isPublic) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const isRefreshRequest = original?.url?.endsWith('/auth/refresh/');

    if (error.response?.status === 401 && !original?._retry && !isRefreshRequest) {
      const refresh = localStorage.getItem('refresh');
      if (refresh) {
        original._retry = true;
        try {
          const response = await axios.post(
            `${api.defaults.baseURL}/auth/refresh/`,
            { refresh },
            { headers: { 'Content-Type': 'application/json' } }
          );
          localStorage.setItem('access', response.data.access);
          original.headers = original.headers || {};
          original.headers.Authorization = `Bearer ${response.data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem('access');
          localStorage.removeItem('refresh');
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;

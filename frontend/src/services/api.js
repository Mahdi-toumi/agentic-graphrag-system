import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const askQuestion = async (query) => {
    const response = await api.post('/ask', { query });
    return response.data;
};

export const getGraphInfo = async () => {
    const response = await api.get('/graph-info');
    return response.data;
};

export const getHealth = async () => {
    const response = await api.get('/');
    return response.data;
};

export default api;

import axios from 'axios';

const baseURL = import.meta.env.VITE_N8N_BASE_URL as string | undefined;
const token = import.meta.env.VITE_N8N_TOKEN as string | undefined;

export const api = axios.create({
	baseURL: baseURL,
	headers: token
		? { Authorization: `Bearer ${token}` }
		: undefined,
});

export const isN8nEnabled = Boolean(baseURL);
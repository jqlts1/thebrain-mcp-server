export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '';

export interface Card {
    thought_id: string;
    name: string;
    interval_days: number;
    ease_factor: number;
    next_review: string;
    state: string;
    tb_modified_at: string;
    next_intervals: number[];
}

export interface ThoughtNode {
    id: string;
    name: string;
    kind?: number;
}

export interface GraphData {
    parents: ThoughtNode[];
    children: ThoughtNode[];
    siblings: ThoughtNode[];
    jumps: ThoughtNode[];
    activeThought: ThoughtNode & { label?: string; note?: string };
    tags: ThoughtNode[];
}

export interface CardDetail extends Card {
    note?: string;
    note_error?: string;
    graph?: GraphData;
}

export interface ReviewResponse {
    success: boolean;
    card: Card;
    quality_label: string;
    interval_before: number;
    interval_after: number;
    next_review: string;
}

export class APIError extends Error {
    status: number;
    constructor(message: string, status: number) {
        super(message);
        this.status = status;
    }
}

function getApiKey(): string | null {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('thebrain_api_key');
    }
    return null;
}

export async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const apiKey = getApiKey();
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
    };

    if (apiKey) {
        headers['Authorization'] = `Bearer ${apiKey}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
            throw new APIError('需要 API Key', 401);
        }
        throw new APIError(`API 错误: ${response.status}`, response.status);
    }

    return response.json();
}

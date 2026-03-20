/**
 * API client for Spam Detection Backend
 */

import type {
  PredictionRequest,
  PredictionResponse,
  BatchPredictionRequest,
  BatchPredictionResponse,
  HealthResponse,
  ApiInfo,
  SpamProbabilityResponse,
} from '@/types/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  /**
   * Get API information
   */
  async getApiInfo(): Promise<ApiInfo> {
    return this.request<ApiInfo>('/')
  }

  /**
   * Check API and model health
   */
  async checkHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health')
  }

  /**
   * Classify a single message as spam or ham
   */
  async predict(request: PredictionRequest): Promise<PredictionResponse> {
    return this.request<PredictionResponse>('/predict', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  /**
   * Classify multiple messages as spam or ham
   */
  async predictBatch(request: BatchPredictionRequest): Promise<BatchPredictionResponse> {
    return this.request<BatchPredictionResponse>('/predict/batch', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  /**
   * Get spam probability for a message
   */
  async getSpamProbability(text: string): Promise<SpamProbabilityResponse> {
    return this.request<SpamProbabilityResponse>(`/predict/probability?text=${encodeURIComponent(text)}`)
  }
}

export const apiClient = new ApiClient()
export default apiClient

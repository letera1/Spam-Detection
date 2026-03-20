/**
 * API types for Spam Detection Backend
 */

export interface PredictionRequest {
  text: string
  threshold?: number
}

export interface BatchPredictionRequest {
  texts: string[]
  threshold?: number
}

export interface PredictionResponse {
  text: string
  label: 'spam' | 'ham'
  confidence: number
  probabilities: {
    spam: number
    ham: number
  }
}

export interface BatchPredictionResponse {
  results: PredictionResponse[]
  total: number
  spam_count: number
  ham_count: number
}

export interface HealthResponse {
  status: 'healthy' | 'degraded'
  model_loaded: boolean
  model_path: string | null
}

export interface ApiInfo {
  name: string
  version: string
  docs: string
  health: string
  predict: string
  batch_predict: string
}

export interface SpamProbabilityResponse {
  text: string
  spam_probability: number
}

'use client'

import { useState } from 'react'
import apiClient from '@/lib/api'
import type { BatchPredictionResponse, PredictionResponse } from '@/types/api'
import BatchResults from '@/components/BatchResults'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function BatchPredictionPage() {
  const [inputText, setInputText] = useState('')
  const [threshold, setThreshold] = useState(0.5)
  const [result, setResult] = useState<BatchPredictionResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim()) return

    const texts = inputText
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)

    if (texts.length === 0) return
    if (texts.length > 100) {
      setError('Maximum 100 messages allowed per batch')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await apiClient.predictBatch({ texts, threshold })
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Batch prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setInputText('')
    setResult(null)
    setError(null)
  }

  const handleLoadExample = () => {
    const examples = [
      'Congratulations! You\'ve won a $1000 gift card. Click here to claim!',
      'Hey, are we still meeting for lunch tomorrow?',
      'URGENT! Your account will be suspended. Verify now!',
      'Thanks for your help yesterday. See you soon!',
      'FREE ENTRY to win FA Cup tickets. Text YES to 87139!',
      'Can you pick up groceries on your way home?',
      'Your package delivery failed. Click to reschedule: bit.ly/xyz',
      'Happy birthday! Hope you have a great day!',
    ]
    setInputText(examples.join('\n'))
  }

  const messages = inputText
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Batch Prediction
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Analyze multiple messages at once. Enter each message on a new line (up to 100 messages per batch).
        </p>
      </div>

      {/* Input Form */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 sm:p-8 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="messages" className="block text-sm font-medium text-gray-700 mb-2">
              Messages (one per line)
            </label>
            <textarea
              id="messages"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter messages here, one per line..."
              rows={10}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none transition-shadow font-mono text-sm"
            />
            <div className="flex justify-between items-center mt-2">
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <span>{messages.length} message(s)</span>
                <span>•</span>
                <span>Max 100 messages</span>
              </div>
              <div className="flex items-center space-x-3">
                {inputText && (
                  <button
                    type="button"
                    onClick={handleClear}
                    className="text-xs text-gray-500 hover:text-gray-700 underline"
                  >
                    Clear All
                  </button>
                )}
                <button
                  type="button"
                  onClick={handleLoadExample}
                  className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                >
                  Load Examples
                </button>
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="threshold" className="block text-sm font-medium text-gray-700 mb-2">
              Classification Threshold: {threshold.toFixed(2)}
            </label>
            <input
              id="threshold"
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>More Lenient (0.0)</span>
              <span>More Strict (1.0)</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={messages.length === 0 || messages.length > 100 || loading}
            className="w-full py-4 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold rounded-xl shadow-md hover:from-primary-700 hover:to-primary-800 focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {loading ? (
              <span className="flex items-center justify-center space-x-2">
                <LoadingSpinner size="sm" />
                <span>Analyzing {messages.length} message(s)...</span>
              </span>
            ) : (
              <span className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
                <span>Analyze {messages.length > 0 ? `${messages.length} Messages` : 'Messages'}</span>
              </span>
            )}
          </button>
        </form>

        {/* Error Display */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-start space-x-3">
              <svg
                className="w-5 h-5 text-red-500 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Validation Warning */}
        {messages.length > 100 && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
            <div className="flex items-start space-x-3">
              <svg
                className="w-5 h-5 text-yellow-500 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-yellow-800">Too Many Messages</h3>
                <p className="text-sm text-yellow-700 mt-1">
                  You have {messages.length} messages. Please reduce to 100 or fewer.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {result && <BatchResults result={result} />}
    </div>
  )
}

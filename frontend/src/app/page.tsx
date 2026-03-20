'use client'

import { useState } from 'react'
import apiClient from '@/lib/api'
import type { PredictionResponse } from '@/types/api'
import PredictionResult from '@/components/PredictionResult'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function Home() {
  const [text, setText] = useState('')
  const [threshold, setThreshold] = useState(0.5)
  const [result, setResult] = useState<PredictionResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await apiClient.predict({ text: text.trim(), threshold })
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setText('')
    setResult(null)
    setError(null)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Detect Spam Messages
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Enter any text message below and our AI-powered system will classify it as spam or ham
          (legitimate message) with confidence scores.
        </p>
      </div>

      {/* Input Form */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 sm:p-8 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
              Message Text
            </label>
            <textarea
              id="message"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter the message you want to analyze..."
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none transition-shadow"
              maxLength={10000}
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-gray-500">
                {text.length.toLocaleString()} / 10,000 characters
              </span>
              {text && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="text-xs text-gray-500 hover:text-gray-700 underline"
                >
                  Clear
                </button>
              )}
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
            disabled={!text.trim() || loading}
            className="w-full py-4 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold rounded-xl shadow-md hover:from-primary-700 hover:to-primary-800 focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {loading ? (
              <span className="flex items-center justify-center space-x-2">
                <LoadingSpinner size="sm" />
                <span>Analyzing...</span>
              </span>
            ) : (
              <span className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <span>Analyze Message</span>
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
      </div>

      {/* Result Display */}
      {result && <PredictionResult result={result} />}

      {/* Example Messages */}
      <div className="mt-12">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Try Example Messages</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {[
            { text: 'Congratulations! You\'ve won a $1000 gift card. Click here to claim!', type: 'spam' },
            { text: 'Hey, are we still meeting for lunch tomorrow?', type: 'ham' },
            { text: 'URGENT! Your account will be suspended. Verify now!', type: 'spam' },
            { text: 'Thanks for your help yesterday. See you soon!', type: 'ham' },
          ].map((example, index) => (
            <button
              key={index}
              onClick={() => setText(example.text)}
              className="p-4 text-left bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl transition-colors group"
            >
              <div className="flex items-center space-x-2 mb-2">
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full ${
                    example.type === 'spam'
                      ? 'bg-spam-100 text-spam-700'
                      : 'bg-ham-100 text-ham-700'
                  }`}
                >
                  {example.type.toUpperCase()}
                </span>
              </div>
              <p className="text-sm text-gray-700 group-hover:text-gray-900 line-clamp-2">
                {example.text}
              </p>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

'use client'

import type { PredictionResponse } from '@/types/api'

interface PredictionResultProps {
  result: PredictionResponse
}

export default function PredictionResult({ result }: PredictionResultProps) {
  const isSpam = result.label === 'spam'
  const spamProbability = result.probabilities.spam * 100
  const hamProbability = result.probabilities.ham * 100

  return (
    <div
      className={`bg-white rounded-2xl shadow-lg border-2 overflow-hidden ${
        isSpam ? 'border-spam-300' : 'border-ham-300'
      }`}
    >
      {/* Header */}
      <div
        className={`px-6 py-4 ${
          isSpam ? 'bg-spam-50' : 'bg-ham-50'
        } border-b ${isSpam ? 'border-spam-200' : 'border-ham-200'}`}
      >
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Analysis Result</h3>
          <span
            className={`inline-flex items-center px-4 py-2 text-sm font-bold rounded-full ${
              isSpam
                ? 'bg-spam-500 text-white'
                : 'bg-ham-500 text-white'
            }`}
          >
            {isSpam ? (
              <>
                <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                SPAM
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                HAM
              </>
            )}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Message Preview */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Message</h4>
          <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
            <p className="text-gray-800 whitespace-pre-wrap break-words">{result.text}</p>
          </div>
        </div>

        {/* Confidence */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Confidence Score</h4>
          <div className="text-3xl font-bold text-gray-900 mb-2">
            {(result.confidence * 100).toFixed(1)}%
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full confidence-bar rounded-full transition-all duration-500 ${
                isSpam ? 'bg-spam-500' : 'bg-ham-500'
              }`}
              style={{ width: `${result.confidence * 100}%` }}
            />
          </div>
        </div>

        {/* Probability Breakdown */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Probability Breakdown</h4>
          <div className="space-y-3">
            {/* Spam Probability */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-spam-700 font-medium">Spam</span>
                <span className="text-gray-600">{spamProbability.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                <div
                  className="h-full bg-spam-500 rounded-full confidence-bar"
                  style={{ width: `${spamProbability}%` }}
                />
              </div>
            </div>

            {/* Ham Probability */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-ham-700 font-medium">Ham (Legitimate)</span>
                <span className="text-gray-600">{hamProbability.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                <div
                  className="h-full bg-ham-500 rounded-full confidence-bar"
                  style={{ width: `${hamProbability}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Info Note */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="flex items-start space-x-3">
            <svg
              className="w-5 h-5 text-blue-500 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-sm text-blue-800">
              <strong>Threshold:</strong> Messages with spam probability above your threshold (
              {(result.confidence * 100).toFixed(0)}%) are classified as spam.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

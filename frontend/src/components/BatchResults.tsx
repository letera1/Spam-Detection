'use client'

import type { BatchPredictionResponse, PredictionResponse } from '@/types/api'
import { useState } from 'react'

interface BatchResultsProps {
  result: BatchPredictionResponse
}

export default function BatchResults({ result }: BatchResultsProps) {
  const [filter, setFilter] = useState<'all' | 'spam' | 'ham'>('all')

  const filteredResults = result.results.filter((r) => {
    if (filter === 'all') return true
    return r.label === filter
  })

  const spamPercentage = (result.spam_count / result.total) * 100
  const hamPercentage = (result.ham_count / result.total) * 100

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Summary Header */}
      <div className="bg-gradient-to-r from-primary-50 to-primary-100 px-6 py-4 border-b border-primary-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Batch Results Summary
          </h3>
          <span className="text-sm text-gray-600">
            {result.total} message(s) analyzed
          </span>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 p-6 bg-gray-50 border-b border-gray-200">
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-900">{result.total}</div>
          <div className="text-sm text-gray-600 mt-1">Total</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-spam-600">{result.spam_count}</div>
          <div className="text-sm text-gray-600 mt-1">Spam ({spamPercentage.toFixed(1)}%)</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-ham-600">{result.ham_count}</div>
          <div className="text-sm text-gray-600 mt-1">Ham ({hamPercentage.toFixed(1)}%)</div>
        </div>
      </div>

      {/* Visual Bar */}
      <div className="h-3 w-full flex">
        <div
          className="bg-spam-500 transition-all duration-500"
          style={{ width: `${spamPercentage}%` }}
        />
        <div
          className="bg-ham-500 transition-all duration-500"
          style={{ width: `${hamPercentage}%` }}
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-gray-200">
        {(['all', 'spam', 'ham'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              filter === f
                ? 'bg-white text-primary-700 border-b-2 border-primary-500'
                : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
            }`}
          >
            {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
            {f === 'spam' && ` (${result.spam_count})`}
            {f === 'ham' && ` (${result.ham_count})`}
            {f === 'all' && ` (${result.total})`}
          </button>
        ))}
      </div>

      {/* Results List */}
      <div className="max-h-[600px] overflow-y-auto">
        {filteredResults.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No messages match the selected filter.
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredResults.map((item, index) => (
              <ResultItem key={index} result={item} index={index} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function ResultItem({ result, index }: { result: PredictionResponse; index: number }) {
  const [expanded, setExpanded] = useState(false)
  const isSpam = result.label === 'spam'

  return (
    <div className="p-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-gray-500">#{index + 1}</span>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full ${
                isSpam
                  ? 'bg-spam-100 text-spam-800'
                  : 'bg-ham-100 text-ham-800'
              }`}
            >
              {isSpam ? 'SPAM' : 'HAM'}
            </span>
            <span className="text-xs text-gray-500">
              {(result.confidence * 100).toFixed(0)}% confidence
            </span>
          </div>
          <p className={`text-gray-800 ${expanded ? '' : 'line-clamp-2'}`}>
            {result.text}
          </p>
          {result.text.length > 100 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-primary-600 hover:text-primary-700 mt-1"
            >
              {expanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>

        {/* Mini Probability Bar */}
        <div className="flex-shrink-0 w-32">
          <div className="flex h-2 rounded-full overflow-hidden">
            <div
              className="bg-spam-500"
              style={{ width: `${result.probabilities.spam * 100}%` }}
            />
            <div
              className="bg-ham-500"
              style={{ width: `${result.probabilities.ham * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>S: {(result.probabilities.spam * 100).toFixed(0)}%</span>
            <span>H: {(result.probabilities.ham * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'
import apiClient from '@/lib/api'
import StatusBadge from './StatusBadge'

export default function Header() {
  const pathname = usePathname()
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await apiClient.checkHealth()
        setIsHealthy(health.model_loaded)
      } catch {
        setIsHealthy(false)
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const navLinks = [
    { href: '/', label: 'Single Prediction' },
    { href: '/batch', label: 'Batch Prediction' },
  ]

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Spam Detection</h1>
              <p className="text-xs text-gray-500">AI-Powered Classification</p>
            </div>
          </Link>

          <nav className="flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  pathname === link.href
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {link.label}
              </Link>
            ))}
            <div className="ml-4 pl-4 border-l border-gray-200">
              <StatusBadge isHealthy={isHealthy} />
            </div>
          </nav>
        </div>
      </div>
    </header>
  )
}

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <svg className="w-5 h-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                clipRule="evenodd"
              />
            </svg>
            <span>Built with Next.js 16 & Tailwind CSS</span>
          </div>
          <div className="flex items-center space-x-6 text-sm text-gray-500">
            <span>Powered by Machine Learning</span>
            <span className="hidden md:inline">•</span>
            <span className="hidden md:inline">FastAPI Backend</span>
          </div>
        </div>
      </div>
    </footer>
  )
}

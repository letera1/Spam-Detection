# Spam Detection Frontend

A modern, responsive web interface for the Spam Detection API built with Next.js 16, Tailwind CSS, and TypeScript.

## Features

- **Single Message Prediction**: Analyze individual text messages for spam classification
- **Batch Prediction**: Process up to 100 messages simultaneously
- **Real-time Health Monitoring**: Automatic API status checking
- **Confidence Visualization**: Clear probability breakdowns with animated progress bars
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark Mode Ready**: Built with theming support

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **HTTP Client**: Fetch API

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Spam Detection API running (backend)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── batch/              # Batch prediction page
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   ├── loading.tsx         # Loading state
│   │   └── page.tsx            # Home page (single prediction)
│   ├── components/             # Reusable React components
│   │   ├── BatchResults.tsx    # Batch results display
│   │   ├── Footer.tsx          # Footer component
│   │   ├── Header.tsx          # Header with navigation
│   │   ├── LoadingSpinner.tsx  # Loading spinner
│   │   ├── PredictionResult.tsx # Single result display
│   │   └── StatusBadge.tsx     # API health indicator
│   ├── lib/                    # Utilities and libraries
│   │   └── api.ts              # API client
│   └── types/                  # TypeScript type definitions
│       └── api.ts              # API types
├── public/                     # Static assets
├── .env.local                  # Environment variables
├── next.config.ts              # Next.js configuration
├── package.json                # Dependencies
├── postcss.config.js           # PostCSS configuration
├── tailwind.config.ts          # Tailwind CSS configuration
└── tsconfig.json               # TypeScript configuration
```

## Available Scripts

```bash
# Development
npm run dev          # Start development server

# Production
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
```

## API Integration

The frontend communicates with the backend API at the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/predict` | POST | Single prediction |
| `/predict/batch` | POST | Batch prediction |
| `/predict/probability` | GET | Spam probability |

## Pages

### Home Page (`/`)
- Single message input form
- Threshold slider for classification sensitivity
- Real-time result display with confidence scores
- Example messages for quick testing

### Batch Prediction (`/batch`)
- Multi-line text input for batch processing
- Support for up to 100 messages
- Filter results by spam/ham
- Summary statistics with visual breakdown

## Customization

### Theme Colors

Edit `tailwind.config.ts` to customize colors:

```typescript
theme: {
  extend: {
    colors: {
      primary: { /* ... */ },
      spam: { /* ... */ },
      ham: { /* ... */ },
    },
  },
}
```

### API URL

Change the API endpoint in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://your-api-server:8000
```

## Screenshots

The application features:
- Clean, modern UI with gradient accents
- Color-coded results (red for spam, green for ham)
- Animated confidence bars
- Responsive layout for all screen sizes

## License

MIT License

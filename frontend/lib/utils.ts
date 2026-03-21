import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatConfidence(value: number): string {
  if (value >= 0.9) return "Very High";
  if (value >= 0.7) return "High";
  if (value >= 0.5) return "Moderate";
  return "Low";
}

export function getConfidenceColor(value: number): string {
  if (value >= 0.8) return "text-green-600 dark:text-green-400";
  if (value >= 0.6) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

export function getLabelColor(label: string): string {
  return label === "spam"
    ? "text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30"
    : "text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30";
}

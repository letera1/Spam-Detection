import { PredictionResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeMessage(
  text: string,
  threshold: number = 0.5
): Promise<PredictionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text,
        threshold,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to analyze message");
    }

    return response.json();
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

export async function predictMessage(
  text: string,
  threshold: number = 0.5
): Promise<PredictionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text,
        threshold,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to predict message");
    }

    return response.json();
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

export async function checkHealth(): Promise<{
  status: string;
  model_loaded: boolean;
  model_path: string | null;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error("Health check failed");
    }

    return response.json();
  } catch (error) {
    console.error("Health check error:", error);
    throw error;
  }
}

export async function getSpamProbability(
  text: string
): Promise<{ text: string; spam_probability: number }> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/predict/probability?text=${encodeURIComponent(text)}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to get probability");
    }

    return response.json();
  } catch (error) {
    console.error("Probability error:", error);
    throw error;
  }
}

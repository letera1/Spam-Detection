export interface SpamFeatures {
  has_urls: boolean;
  url_count: number;
  has_emails: boolean;
  has_phone: boolean;
  has_money_symbols: boolean;
  money_count: number;
  has_excessive_punctuation: boolean;
  has_all_caps: boolean;
  emoji_count: number;
  has_suspicious_words: boolean;
  suspicious_word_count: number;
  exclamation_count: number;
  question_count: number;
  avg_word_length: number;
  char_to_word_ratio: number;
}

export interface PredictionResponse {
  text: string;
  label: "spam" | "ham";
  confidence: number;
  probabilities: {
    ham: number;
    spam: number;
  };
  features?: SpamFeatures;
  explanation?: string;
}

export interface AnalysisHistory {
  id: string;
  text: string;
  label: "spam" | "ham";
  confidence: number;
  timestamp: Date;
  features?: SpamFeatures;
}

export interface Stats {
  totalAnalyses: number;
  spamCount: number;
  hamCount: number;
  avgConfidence: number;
}

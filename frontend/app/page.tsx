"use client";

import { useState, useEffect, useCallback } from "react";
import { analyzeMessage, checkHealth } from "@/lib/api";
import { PredictionResponse, AnalysisHistory, Stats } from "@/lib/types";
import { cn, formatPercentage, formatConfidence, getConfidenceColor, getLabelColor } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  Send,
  History,
  BarChart3,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Loader2,
  Trash2,
  Moon,
  Sun,
  RefreshCw,
  Info,
} from "lucide-react";

export default function Home() {
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [health, setHealth] = useState<{ status: string; model_loaded: boolean } | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<"analyze" | "history" | "stats">("analyze");

  // Load history and theme from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem("spamAnalysisHistory");
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      setDarkMode(true);
      document.documentElement.classList.add("dark");
    }

    // Check API health
    checkHealth()
      .then((data) => setHealth(data))
      .catch(() => setHealth({ status: "error", model_loaded: false }));
  }, []);

  // Save history to localStorage
  useEffect(() => {
    localStorage.setItem("spamAnalysisHistory", JSON.stringify(history));
  }, [history]);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  // Analyze message
  const handleAnalyze = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await analyzeMessage(inputText);
      setResult(response);

      // Add to history
      const newEntry: AnalysisHistory = {
        id: Date.now().toString(),
        text: inputText,
        label: response.label,
        confidence: response.confidence,
        timestamp: new Date(),
        features: response.features,
      };
      setHistory((prev) => [newEntry, ...prev.slice(0, 49)]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze message");
    } finally {
      setLoading(false);
    }
  };

  // Clear history
  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem("spamAnalysisHistory");
  };

  // Calculate stats
  const stats: Stats = {
    totalAnalyses: history.length,
    spamCount: history.filter((h) => h.label === "spam").length,
    hamCount: history.filter((h) => h.label === "ham").length,
    avgConfidence:
      history.length > 0
        ? history.reduce((acc, h) => acc + h.confidence, 0) / history.length
        : 0,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Spam Detector
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                AI-Powered Message Analysis
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Health Indicator */}
            {health && (
              <Badge variant={health.model_loaded ? "success" : "destructive"}>
                {health.model_loaded ? (
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                ) : (
                  <XCircle className="h-3 w-3 mr-1" />
                )}
                {health.model_loaded ? "Model Ready" : "Model Not Loaded"}
              </Badge>
            )}

            {/* Theme Toggle */}
            <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
              {darkMode ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6">
          <Button
            variant={activeTab === "analyze" ? "default" : "outline"}
            onClick={() => setActiveTab("analyze")}
            className="gap-2"
          >
            <ShieldCheck className="h-4 w-4" />
            Analyze
          </Button>
          <Button
            variant={activeTab === "history" ? "default" : "outline"}
            onClick={() => setActiveTab("history")}
            className="gap-2"
          >
            <History className="h-4 w-4" />
            History
            {history.length > 0 && (
              <Badge variant="secondary" className="ml-1">
                {history.length}
              </Badge>
            )}
          </Button>
          <Button
            variant={activeTab === "stats" ? "default" : "outline"}
            onClick={() => setActiveTab("stats")}
            className="gap-2"
          >
            <BarChart3 className="h-4 w-4" />
            Statistics
          </Button>
        </div>

        {/* Analyze Tab */}
        {activeTab === "analyze" && (
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Input Card */}
            <Card>
              <CardHeader>
                <CardTitle>Message Input</CardTitle>
                <CardDescription>
                  Enter the message you want to analyze for spam detection
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Enter message text here..."
                  className="w-full h-40 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {inputText.length} characters
                  </span>
                  <Button
                    onClick={handleAnalyze}
                    disabled={loading || !inputText.trim()}
                    className="gap-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4" />
                        Analyze
                      </>
                    )}
                  </Button>
                </div>

                {error && (
                  <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
                    <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                  </div>
                )}

                {!health?.model_loaded && (
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg flex items-start gap-2">
                    <Info className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-yellow-600 dark:text-yellow-400">
                      Model not loaded. Please train a model first by running:{" "}
                      <code className="bg-yellow-100 dark:bg-yellow-900/40 px-1 rounded">
                        python main.py train
                      </code>
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Result Card */}
            <Card>
              <CardHeader>
                <CardTitle>Analysis Result</CardTitle>
                <CardDescription>
                  AI-powered spam detection results
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!result ? (
                  <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-500">
                    <div className="text-center">
                      <Shield className="h-16 w-16 mx-auto mb-4 opacity-50" />
                      <p>Enter a message and click Analyze to see results</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Label Badge */}
                    <div className="flex items-center justify-center">
                      <Badge
                        className={cn(
                          "text-lg px-6 py-3",
                          getLabelColor(result.label)
                        )}
                      >
                        {result.label === "spam" ? (
                          <ShieldAlert className="h-5 w-5 mr-2" />
                        ) : (
                          <ShieldCheck className="h-5 w-5 mr-2" />
                        )}
                        {result.label.toUpperCase()}
                      </Badge>
                    </div>

                    {/* Confidence */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Confidence
                        </span>
                        <span
                          className={cn(
                            "text-sm font-bold",
                            getConfidenceColor(result.confidence)
                          )}
                        >
                          {formatConfidence(result.confidence)}
                        </span>
                      </div>
                      <Progress value={result.confidence * 100} className="h-3" />
                      <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                        {formatPercentage(result.confidence)}
                      </p>
                    </div>

                    {/* Probabilities */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Ham Probability
                        </p>
                        <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {formatPercentage(result.probabilities.ham)}
                        </p>
                      </div>
                      <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Spam Probability
                        </p>
                        <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                          {formatPercentage(result.probabilities.spam)}
                        </p>
                      </div>
                    </div>

                    {/* Explanation */}
                    {result.explanation && (
                      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <p className="text-sm text-blue-800 dark:text-blue-200">
                          {result.explanation}
                        </p>
                      </div>
                    )}

                    {/* Features */}
                    {result.features && (
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Detected Features
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {result.features.has_urls && (
                            <Badge variant="outline">URLs</Badge>
                          )}
                          {result.features.has_emails && (
                            <Badge variant="outline">Emails</Badge>
                          )}
                          {result.features.has_phone && (
                            <Badge variant="outline">Phone</Badge>
                          )}
                          {result.features.has_money_symbols && (
                            <Badge variant="outline">Money</Badge>
                          )}
                          {result.features.has_suspicious_words && (
                            <Badge variant="outline">
                              {result.features.suspicious_word_count} Spam Words
                            </Badge>
                          )}
                          {result.features.has_excessive_punctuation && (
                            <Badge variant="outline">!!!</Badge>
                          )}
                          {result.features.has_all_caps && (
                            <Badge variant="outline">CAPS</Badge>
                          )}
                          {result.features.emoji_count > 0 && (
                            <Badge variant="outline">
                              {result.features.emoji_count} Emojis
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* History Tab */}
        {activeTab === "history" && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Analysis History</CardTitle>
                <CardDescription>
                  Your recent spam detection analyses
                </CardDescription>
              </div>
              {history.length > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearHistory}
                  className="gap-2"
                >
                  <Trash2 className="h-4 w-4" />
                  Clear
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {history.length === 0 ? (
                <div className="text-center py-12 text-gray-400 dark:text-gray-500">
                  <History className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p>No analysis history yet</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900 dark:text-white truncate mb-2">
                            {item.text}
                          </p>
                          <div className="flex items-center gap-2">
                            <Badge
                              className={cn(
                                "text-xs",
                                getLabelColor(item.label)
                              )}
                            >
                              {item.label}
                            </Badge>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {formatPercentage(item.confidence)}
                            </span>
                            <span className="text-xs text-gray-400 dark:text-gray-500">
                              {new Date(item.timestamp).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Stats Tab */}
        {activeTab === "stats" && (
          <div className="space-y-6">
            {/* Overview Cards */}
            <div className="grid gap-4 md:grid-cols-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Total Analyses
                    </p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                      {stats.totalAnalyses}
                    </p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Spam Detected
                    </p>
                    <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
                      {stats.spamCount}
                    </p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Ham Messages
                    </p>
                    <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                      {stats.hamCount}
                    </p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Avg Confidence
                    </p>
                    <p
                      className={cn(
                        "text-3xl font-bold mt-2",
                        getConfidenceColor(stats.avgConfidence)
                      )}
                    >
                      {formatPercentage(stats.avgConfidence)}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Spam vs Ham Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Spam vs Ham Distribution</CardTitle>
                <CardDescription>
                  Breakdown of analyzed messages
                </CardDescription>
              </CardHeader>
              <CardContent>
                {stats.totalAnalyses === 0 ? (
                  <div className="text-center py-12 text-gray-400 dark:text-gray-500">
                    <BarChart3 className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p>No data available yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Spam
                        </span>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {stats.spamCount} ({stats.totalAnalyses > 0 ? formatPercentage(stats.spamCount / stats.totalAnalyses) : "0%"})
                        </span>
                      </div>
                      <Progress
                        value={(stats.spamCount / stats.totalAnalyses) * 100}
                        className="h-3"
                      />
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Ham
                        </span>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {stats.hamCount} ({stats.totalAnalyses > 0 ? formatPercentage(stats.hamCount / stats.totalAnalyses) : "0%"})
                        </span>
                      </div>
                      <Progress
                        value={(stats.hamCount / stats.totalAnalyses) * 100}
                        className="h-3 bg-green-100 dark:bg-green-900/30"
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>AI-Powered Spam Detection System • Built with Next.js & FastAPI</p>
        </div>
      </footer>
    </div>
  );
}

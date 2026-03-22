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
    <div className="min-h-screen relative bg-slate-50 dark:bg-black text-slate-900 dark:text-cyan-50">
      <div className="absolute inset-0 z-0 bg-grid-cyber opacity-40 pointer-events-none"></div>
      <div className="absolute inset-0 z-0 scanline pointer-events-none"></div>
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Header */}
        <header className="sticky top-0 z-50 w-full border-b border-cyan-500/20 bg-white/80 dark:bg-black/80 backdrop-blur">
          <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-2.5 bg-blue-600/10 dark:bg-cyan-900/40 rounded-xl border border-blue-500/30 dark:border-cyan-500/50 shadow-[0_0_15px_rgba(0,255,255,0.2)]">
                <Shield className="h-7 w-7 text-blue-600 dark:text-cyan-400" />
              </div>
              <div>
                <h1 className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-purple-700 dark:from-cyan-400 dark:to-blue-500 tracking-tighter drop-shadow-sm">
                  NexusML SpamGuard
                </h1>
                <p className="text-xs font-bold text-gray-500 dark:text-cyan-600/80 tracking-[0.2em] uppercase mt-1">
                  Threat Detection Protocol V2
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
        <div className="flex gap-3 mb-6 relative z-10 w-fit p-1 bg-black/20 dark:bg-cyan-950/20 backdrop-blur-md rounded-lg border border-gray-200 dark:border-cyan-500/20">
          <Button
            variant={activeTab === "analyze" ? "default" : "ghost"}
            onClick={() => setActiveTab("analyze")}
            className={cn("gap-2 font-mono text-xs tracking-widest", activeTab === "analyze" ? "bg-blue-600 hover:bg-blue-700 dark:bg-cyan-600 dark:text-black dark:hover:bg-cyan-500 shadow-[0_0_15px_rgba(0,255,255,0.4)]" : "text-gray-500 dark:text-cyan-500 hover:text-cyan-400")}
          >
            <ShieldCheck className="h-4 w-4" />
            ANALYZE_FEED
          </Button>
          <Button
            variant={activeTab === "history" ? "default" : "ghost"}
            onClick={() => setActiveTab("history")}
            className={cn("gap-2 font-mono text-xs tracking-widest", activeTab === "history" ? "bg-blue-600 hover:bg-blue-700 dark:bg-cyan-600 dark:text-black dark:hover:bg-cyan-500 shadow-[0_0_15px_rgba(0,255,255,0.4)]" : "text-gray-500 dark:text-cyan-500 hover:text-cyan-400")}
          >
            <History className="h-4 w-4" />
            SYS_LOGS
            {history.length > 0 && (
              <Badge variant="secondary" className="ml-1 bg-black/20 border-black/10">
                {history.length}
              </Badge>
            )}
          </Button>
          <Button
            variant={activeTab === "stats" ? "default" : "ghost"}
            onClick={() => setActiveTab("stats")}
            className={cn("gap-2 font-mono text-xs tracking-widest", activeTab === "stats" ? "bg-blue-600 hover:bg-blue-700 dark:bg-cyan-600 dark:text-black dark:hover:bg-cyan-500 shadow-[0_0_15px_rgba(0,255,255,0.4)]" : "text-gray-500 dark:text-cyan-500 hover:text-cyan-400")}
          >
            <BarChart3 className="h-4 w-4" />
            METRICS
          </Button>
        </div>

        {/* Analyze Tab */}
        {activeTab === "analyze" && (
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Input Card */}
<Card className="backdrop-blur-md bg-white/60 dark:bg-black/40 border border-slate-200 dark:border-cyan-500/30 shadow-[0_4px_20px_rgba(0,255,255,0.05)]">
              <CardHeader>
                <CardTitle className="font-mono flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-cyan-500 animate-pulse"></span>
                  INPUT_DATA_STREAM
                </CardTitle>
                <CardDescription className="dark:text-cyan-600/70 font-mono text-xs">
                  Awaiting payload for heuristic analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="relative group">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg blur opacity-20 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Provide string payload..."
                    className="relative w-full h-40 p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500 dark:border-cyan-500/30 dark:bg-black/80 dark:text-cyan-50 font-mono text-sm shadow-inner transition-all"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-gray-500 dark:text-cyan-600/70">
                    BYTES: {inputText.length}
                  </span>
                  <Button
                    onClick={handleAnalyze}
                    disabled={loading || !inputText.trim()}
                    className="gap-2 bg-blue-600 hover:bg-blue-700 dark:bg-cyan-600 dark:hover:bg-cyan-500 dark:text-black font-bold relative overflow-hidden group"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        PROCESSING...
                      </>
                    ) : (
                      <>
                        <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                        <Send className="h-4 w-4" />
                        INITIATE_SCAN
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
            <Card className="backdrop-blur-md bg-white/60 dark:bg-black/40 border border-slate-200 dark:border-cyan-500/30 shadow-[0_4px_20px_rgba(0,255,255,0.05)] relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <Shield className="h-48 w-48 text-cyan-500" />
              </div>
              <CardHeader className="relative z-10">
                <CardTitle className="font-mono flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-cyan-500" />
                  DIAGNOSTIC_OUTPUT
                </CardTitle>
                <CardDescription className="dark:text-cyan-600/70 font-mono text-xs">
                  Real-time telemetry and classification results
                </CardDescription>
              </CardHeader>
              <CardContent className="relative z-10">
                {!result ? (
                  <div className="h-64 flex flex-col items-center justify-center text-gray-400 dark:text-cyan-600/50 font-mono">
                    <div className="relative">
                      <Shield className="h-16 w-16 mx-auto mb-4 opacity-20" />
                      <div className="absolute inset-0 border border-cyan-500/20 rounded-full animate-[ping_3s_infinite] opacity-0 dark:opacity-100"></div>
                    </div>
                    <p className="tracking-widest text-xs">&gt; AWAITING_INPUT_STREAM...</p>
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
                    <div className="grid grid-cols-2 gap-4 font-mono">
                      <div className="p-4 bg-green-50 dark:bg-green-950/40 rounded-lg border border-green-200 dark:border-green-500/30">
                        <p className="text-[10px] text-gray-500 dark:text-green-500/70 mb-1 tracking-widest uppercase">
                          SYS.HAM_PROBABILITY
                        </p>
                        <p className="text-3xl font-light text-green-600 dark:text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]">
                          {formatPercentage(result.probabilities.ham)}
                        </p>
                      </div>
                      <div className="p-4 bg-red-50 dark:bg-red-950/40 rounded-lg border border-red-200 dark:border-red-500/30">
                        <p className="text-[10px] text-gray-500 dark:text-red-500/70 mb-1 tracking-widest uppercase">
                          SYS.SPAM_PROBABILITY
                        </p>
                        <p className="text-3xl font-light text-red-600 dark:text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]">
                          {formatPercentage(result.probabilities.spam)}
                        </p>
                      </div>
                    </div>

                    {/* Explanation */}
                    {result.explanation && (
                      <div className="p-4 bg-blue-50 dark:bg-cyan-950/20 border-l-4 border-blue-500 dark:border-cyan-500 rounded-lg">
                        <p className="text-sm font-mono text-blue-800 dark:text-cyan-200">
                          <span className="font-bold mr-2 text-blue-700 dark:text-cyan-400">LOG:</span> 
                          {result.explanation}
                        </p>
                      </div>
                    )}

                    {/* Features */}
                    {result.features && (
                      <div className="space-y-3 pt-2 border-t border-gray-200 dark:border-cyan-500/20">
                        <h4 className="text-xs font-mono text-gray-700 dark:text-cyan-500/70 tracking-widest uppercase">
                          Detected_Payload_Signatures
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
          <Card className="backdrop-blur-md bg-white/60 dark:bg-black/40 border border-slate-200 dark:border-cyan-500/30 shadow-[0_4px_20px_rgba(0,255,255,0.05)]">
            <CardHeader className="flex flex-row items-center justify-between border-b border-gray-200 dark:border-cyan-500/20 pb-4">
              <div>
                <CardTitle className="font-mono flex items-center gap-2">
                  <span className="h-2 w-2 bg-yellow-500 rounded-sm"></span>
                  SYSTEM_LOGS
                </CardTitle>
                <CardDescription className="dark:text-cyan-600/70 font-mono text-xs">
                  Historical chronologies of intercepted messages
                </CardDescription>
              </div>
              {history.length > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearHistory}
                  className="gap-2 dark:border-red-500/30 dark:text-red-400 dark:hover:bg-red-500/10 font-mono text-xs"
                >
                  <Trash2 className="h-4 w-4" />
                  PURGE_LOGS
                </Button>
              )}
            </CardHeader>
            <CardContent className="pt-6">
              {history.length === 0 ? (
                <div className="text-center py-12 text-gray-400 dark:text-cyan-600/40 font-mono">
                  <History className="h-16 w-16 mx-auto mb-4 opacity-30" />
                  <p className="tracking-widest text-sm">NO_DATA_FOUND</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="p-4 border border-gray-200 dark:border-cyan-500/20 rounded-lg hover:bg-gray-50 dark:hover:bg-cyan-900/10 transition-colors bg-white/50 dark:bg-black/50 backdrop-blur-sm"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-mono text-gray-900 dark:text-gray-300 truncate mb-2">
                            <span className="text-cyan-600 dark:text-cyan-500 mr-2 opacity-50">&gt;</span>
                            {item.text}
                          </p>
                          <div className="flex items-center gap-3">
                            <Badge
                              className={cn(
                                "text-[10px] font-mono",
                                getLabelColor(item.label)
                              )}
                            >
                              {item.label}
                            </Badge>
                            <span className="text-[10px] font-mono text-gray-500 dark:text-cyan-600/70 border-l border-gray-300 dark:border-cyan-800 pl-3">
                              CONF: {formatPercentage(item.confidence)}
                            </span>
                            <span className="text-[10px] font-mono text-gray-400 dark:text-cyan-600/50 border-l border-gray-300 dark:border-cyan-800 pl-3">
                              {new Date(item.timestamp).toISOString()}
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
              <Card className="backdrop-blur-md bg-white/60 dark:bg-black/40 border border-slate-200 dark:border-blue-500/30">
                <CardContent className="pt-6">
                  <div className="text-center font-mono">
                    <p className="text-xs text-gray-500 dark:text-blue-500/70 tracking-widest uppercase">
                      TOTAL_ANALYSES
                    </p>
                    <p className="text-3xl font-light text-gray-900 dark:text-blue-400 mt-2 drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]">
                      {stats.totalAnalyses}
                    </p>
                  </div>
                </CardContent>
              </Card>
              <Card className="backdrop-blur-md bg-white/60 dark:bg-black/40 border border-slate-200 dark:border-red-500/30">
                <CardContent className="pt-6">
                  <div className="text-center font-mono">
                    <p className="text-xs text-gray-500 dark:text-red-500/70 tracking-widest uppercase">
                      THREATS_DETECTED
                    </p>
                    <p className="text-3xl font-light text-red-600 dark:text-red-400 mt-2 drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]">
                      {stats.spamCount}
                    </p>
                  </div>
                </CardContent>
              </Card>
              <Card className="backdrop-blur-md bg-white/60 dark:bg-black/40 border border-slate-200 dark:border-green-500/30">
                <CardContent className="pt-6">
                  <div className="text-center font-mono">
                    <p className="text-xs text-gray-500 dark:text-green-500/70 tracking-widest uppercase">
                      SAFE_MESSAGES
                    </p>
                    <p className="text-3xl font-light text-green-600 dark:text-green-400 mt-2 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]">
                      {stats.hamCount}
                    </p>
                  </div>
                </CardContent>
              </Card>
              <Card className="backdrop-blur-md bg-white/60 dark:bg-black/40 border border-slate-200 dark:border-cyan-500/30">
                <CardContent className="pt-6">
                  <div className="text-center font-mono">
                    <p className="text-xs text-gray-500 dark:text-cyan-500/70 tracking-widest uppercase">
                      AVG_CONFIDENCE
                    </p>
                    <p
                      className={cn(
                        "text-3xl font-light mt-2 drop-shadow-md",
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
            <Card className="backdrop-blur-md bg-white/60 dark:bg-black/40 border border-slate-200 dark:border-purple-500/30">
              <CardHeader>
                <CardTitle className="font-mono text-purple-400">DISTRIBUTION_METRICS</CardTitle>
                <CardDescription className="font-mono text-xs dark:text-purple-500/70">
                  Global telemetry dataset visualization
                </CardDescription>
              </CardHeader>
              <CardContent>
                {stats.totalAnalyses === 0 ? (
                  <div className="text-center py-12 text-gray-400 dark:text-purple-500/30 font-mono">
                    <BarChart3 className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p className="tracking-widest text-sm">INSUFFICIENT_DATA</p>
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
      <footer className="border-t border-cyan-500/20 mt-auto bg-black/40 backdrop-blur">
        <div className="container mx-auto px-4 py-6 text-center text-xs font-mono text-gray-500 dark:text-cyan-600/70">
          <p>NEXUS-ML // THREAT INTELLIGENCE SYSTEMS // SECURE CONNECTION ESTABLISHED</p>
        </div>
      </footer>
      </div>
    </div>
  );
}

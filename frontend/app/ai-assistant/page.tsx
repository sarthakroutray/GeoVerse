"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { MessageCircle, Send, Sparkles } from "lucide-react"
import Navbar from "@/components/navbar"
import { useTheme } from "@/components/theme-provider"

// ☀️ Light Theme Background Animation
function EnhancedBackground({ isDark }: { isDark: boolean }) {
  if (!isDark) {
    return (
      <div className="light-mode-background absolute inset-0 -z-10">
        <div className="light-sky-gradient" />
        <div className="light-clouds">
          <div className="cloud cloud-1" />
          <div className="cloud cloud-2" />
          <div className="cloud cloud-3" />
          <div className="cloud cloud-4" />
        </div>
        <div className="light-rays">
          <div className="ray ray-1" />
          <div className="ray ray-2" />
          <div className="ray ray-3" />
        </div>
        <div className="floating-elements">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="floating-dot"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${8 + Math.random() * 4}s`,
              }}
            />
          ))}
        </div>
      </div>
    )
  }
  return null
}

export default function AIAssistantPage() {
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const [chatMessage, setChatMessage] = useState("")
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string; sources?: any[] }>>([
    { role: 'assistant', content: "Hello! I'm your GeoVerse AI assistant. Ask me about satellite data, weather patterns, or any geospatial information you need." }
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement | null>(null)

  async function sendMessage() {
    if (!chatMessage.trim() || loading) return
    const userText = chatMessage.trim()
    setChatMessage("")
    setMessages(prev => [...prev, { role: 'user', content: userText }])
    setLoading(true)
    setError(null)
    try {
      const { chatRequest } = await import("@/lib/api")
      const res = await chatRequest({ message: userText })
      setMessages(prev => [...prev, { role: 'assistant', content: res.response, sources: res.sources }])
    } catch (e: any) {
      setError(e.message || 'Failed to get response')
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong contacting the backend.' }])
    } finally {
      setLoading(false)
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
    }
  }

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const quickSuggestions = [
    "Rainfall in Delhi today",
    "Current NDVI map",
    "Satellite coverage India",
    "Weather patterns Mumbai",
    "Land use changes 2024",
  ]

  return (
    <div
      className={`min-h-screen relative ${isDark ? "bg-black" : "bg-white"}`}
      style={{
        backgroundImage: isDark ? `url("/star_nyt.jpg")` : undefined,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <Navbar />

      {/* ☀️ Light Mode Enhanced Background */}
      <EnhancedBackground isDark={isDark} />

      {/* Dark overlay for readability */}
      {isDark && <div className="absolute inset-0 bg-black/60 z-0" />}

      <main className="container mx-auto px-4 pt-24 pb-16 relative z-10">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-800 dark:text-white mb-4">
            <Sparkles className="inline-block mr-3 h-8 w-8 text-blue-600 dark:text-blue-400" />
            GeoVerse AI Assistant
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Ask me anything about satellite data, weather, land use, or real-time geospatial events
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Powered by ISRO</p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20 shadow-2xl">
            <CardContent className="p-6 sm:p-8">
              <div className="space-y-6">
                {/* Chat Interface */}
                <div className="bg-gray-100 dark:bg-gray-800/50 rounded-lg p-4 min-h-[300px] max-h-[500px] overflow-y-auto space-y-4">
                  {messages.map((m, idx) => (
                    <div key={idx} className={`flex items-start space-x-3 ${m.role === 'user' ? 'justify-end' : ''}`}>
                      {m.role === 'assistant' && (
                        <div className="bg-blue-600 rounded-full p-2"><MessageCircle className="h-4 w-4 text-white" /></div>
                      )}
                      <div className={`rounded-lg p-3 max-w-[70%] text-sm whitespace-pre-wrap ${m.role === 'assistant' ? 'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200' : 'bg-blue-600 text-white ml-auto'}`}>
                        {m.content}
                        {m.sources && m.sources.length > 0 && (
                          <div className="mt-2 space-y-1">
                            <p className="text-xs font-semibold opacity-70">Sources:</p>
                            {m.sources.slice(0,3).map((s:any,i:number)=>(
                              <a key={i} href={s.url} target="_blank" className="block text-xs underline break-all">• {s.title || s.url}</a>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {loading && <p className="text-xs text-gray-500 animate-pulse">Thinking...</p>}
                  {error && <p className="text-xs text-red-500">{error}</p>}
                  <div ref={bottomRef} />
                </div>

                {/* Input Area */}
                <div className="flex gap-2">
                  <Input
                    placeholder="What's the current weather in Mumbai?"
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    className="flex-1 bg-white/70 dark:bg-white/10 border-white/30 dark:border-white/20 text-gray-800 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400"
                  />
                  <Button className="bg-blue-600 hover:bg-blue-700" disabled={loading} onClick={sendMessage}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                {/* Quick Suggestions */}
                <div className="space-y-3">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Quick suggestions:</p>
                  <div className="flex flex-wrap gap-2">
                    {quickSuggestions.map((suggestion, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="cursor-pointer bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors border-0"
                        onClick={() => { setChatMessage(suggestion); }}
                      >
                        {suggestion}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

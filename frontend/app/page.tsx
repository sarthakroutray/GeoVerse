"use client"

import { useEffect, Suspense, useState, useRef } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Globe, Satellite, Play, Eye, Github, Linkedin, Twitter, Mail, MapPin, User, BarChart3 } from "lucide-react"
import Navbar from "@/components/navbar"
import { useTheme } from "@/components/theme-provider"

// Enhanced Background Component
function EnhancedBackground({ isDark }: { isDark: boolean }) {
  useEffect(() => {
    if (!isDark) return // Only show shooting stars in dark mode

    const createShootingStar = () => {
      const color = "#fff"
      for (let i = 0; i < 2; i++) { // Create two shooting stars at a time
        const shootingStar = document.createElement("div")
        shootingStar.className = "shooting-star"
        shootingStar.style.position = "fixed"
        shootingStar.style.left = Math.random() * 100 + "%"
        shootingStar.style.top = Math.random() * 50 + "%"
        shootingStar.style.width = "3px"
        shootingStar.style.height = "3px"
        shootingStar.style.borderRadius = "50%"
        shootingStar.style.background = color
        shootingStar.style.boxShadow = `0 0 24px 8px ${color}`
        shootingStar.style.zIndex = "1000"
        shootingStar.style.pointerEvents = "none"
        shootingStar.style.animation = "shooting 2.5s linear forwards"
        document.body.appendChild(shootingStar)
        setTimeout(() => {
          if (document.body.contains(shootingStar)) {
            document.body.removeChild(shootingStar)
          }
        }, 2500)
      }
    }

    // Create initial shooting stars
    createShootingStar()
    createShootingStar()

    // Set interval for continuous shooting stars (less frequent)
    const interval = setInterval(createShootingStar, 1500)
    return () => clearInterval(interval)
  }, [isDark])

  if (!isDark) {
    return (
      <div className="light-mode-background">
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

  return (
    <div className="enhanced-starry-bg">
      <div className="night-sky-gradient" />
      <div className="aurora-container">
        <div className="aurora aurora-1" />
        <div className="aurora aurora-2" />
        <div className="aurora aurora-3" />
      </div>
      <div className="stars-layer stars-small">
        {[...Array(300)].map((_, i) => (
          <div
            key={`small-${i}`}
            className="star star-small"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`,
            }}
          />
        ))}
      </div>
      <div className="stars-layer stars-medium">
        {[...Array(150)].map((_, i) => (
          <div
            key={`medium-${i}`}
            className="star star-medium"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              animationDuration: `${3 + Math.random() * 4}s`,
            }}
          />
        ))}
      </div>
      <div className="stars-layer stars-large">
        {[...Array(80)].map((_, i) => (
          <div
            key={`large-${i}`}
            className="star star-large"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${4 + Math.random() * 5}s`,
            }}
          />
        ))}
      </div>
      <div className="constellation-stars">
        {[...Array(30)].map((_, i) => (
          <div
            key={`constellation-${i}`}
            className="star star-constellation"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 6}s`,
            }}
          />
        ))}
      </div>
      <div className="nebula-clouds">
        <div className="nebula-cloud nebula-1" />
        <div className="nebula-cloud nebula-2" />
        <div className="nebula-cloud nebula-3" />
        <div className="nebula-cloud nebula-4" />
        <div className="nebula-cloud nebula-5" />
      </div>
      <div className="milky-way" />
    </div>
  )
}

// Start Exploring Modal
function ExploreModal() {
  const features = [
    { icon: Satellite, title: "Satellite Data", desc: "Access real-time satellite imagery and data" },
    { icon: BarChart3, title: "Weather Analysis", desc: "Get detailed weather patterns and forecasts" },
    { icon: Globe, title: "Vegetation Monitoring", desc: "Track NDVI and forest coverage changes" },
    { icon: Globe, title: "Land Use Mapping", desc: "Analyze land use patterns and urban growth" },
  ]

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          size="lg"
          className="bg-gradient-to-r from-[#2d0036] via-[#3a185a] to-[#1a0026] hover:from-[#3a185a] hover:to-[#2d0036] text-white px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg shadow-xl"
        >
          <Play className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
          Start Exploring
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-2xl bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-white/20">
        <DialogHeader>
          <DialogTitle className="text-center text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Start Your GeoVerse Journey
          </DialogTitle>
        </DialogHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="cosmic-card hover:space-glow transition-all cursor-pointer"
            >
              <CardContent className="p-4 text-center">
                <feature.icon className="h-8 w-8 mx-auto mb-2 text-blue-600 dark:text-blue-400" />
                <h3 className="font-semibold text-gray-800 dark:text-white mb-1">{feature.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-300">{feature.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="mt-6 space-y-3">
          <Link href="/ai-assistant">
            <Button className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
              <User className="mr-2 h-4 w-4" />
              Try AI Assistant
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button
              variant="outline"
              className="w-full border-blue-200 dark:border-white/20 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-white/10 bg-transparent"
            >
              <Eye className="mr-2 h-4 w-4" />
              View Dashboard
            </Button>
          </Link>
        </div>
      </DialogContent>
    </Dialog>
  )
}

function SplineViewerEmbed() {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    // Inject the Spline viewer script if not already present
    if (!document.querySelector('script[src="https://unpkg.com/@splinetool/viewer@1.10.22/build/spline-viewer.js"]')) {
      const script = document.createElement('script')
      script.type = 'module'
      script.src = 'https://unpkg.com/@splinetool/viewer@1.10.22/build/spline-viewer.js'
      document.body.appendChild(script)
    }
    // Inject the spline-viewer element
    if (ref.current && !ref.current.querySelector('spline-viewer')) {
      const viewer = document.createElement('spline-viewer')
      viewer.setAttribute('url', 'https://prod.spline.design/3UzGWg8BpdFpT4XG/scene.splinecode')
      viewer.style.width = '100%'
      viewer.style.height = '100%'
      viewer.style.minHeight = '100%'
      viewer.style.minWidth = '100%'
      viewer.style.border = 'none'
      viewer.style.background = 'transparent'
      ref.current.appendChild(viewer)
    }
  }, [])
  return <div ref={ref} style={{ width: '100%', height: '100%' }} />
}

export default function GeoVersePage() {
  const { theme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const isDark = theme === "dark"

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null // Prevent hydration mismatch
  }

  return (
    <div className="min-h-screen transition-colors duration-300 bg-space-gradient">
      <div className={`min-h-screen ${isDark ? "bg-gray-900" : "bg-white"}`}>
        <EnhancedBackground isDark={isDark} />
        <Navbar />

        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16 bg-black">
          <div className="absolute inset-0" />
          <div className="container mx-auto px-4 z-10">
            <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
              <div className="text-center lg:text-left">
                <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold mb-4 sm:mb-6 text-white drop-shadow-lg">
                  GeoVerse
                </h1>
                <p className="text-xl sm:text-2xl lg:text-3xl text-white mb-3 sm:mb-4 drop-shadow-md">
                Conversational AI for Satellite-Driven Insights.
                </p>
                <p className="text-base sm:text-lg text-gray-300 mb-6 sm:mb-8 max-w-2xl drop-shadow-sm">
                Live access to geospatial insights from ISRO's satellite networks, including weather, ocean, and atmospheric data.
                </p>
                <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center lg:justify-start">
                  <ExploreModal />
                  <Link href="/dashboard">
                    <Button
                      size="lg"
                      variant="outline"
                      className="border-white/40 dark:border-white/30 text-gray-700 dark:text-white hover:bg-white/20 dark:hover:bg-white/10 px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg bg-white/10 dark:bg-white/5 backdrop-blur-sm shadow-xl w-full sm:w-auto"
                    >
                      <Eye className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                      Dashboard Overview
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="relative h-64 sm:h-80 lg:h-[500px] mt-8 lg:mt-0">
                {/* Spline Web Viewer Embed */}
                <div className="w-full h-full rounded-lg overflow-hidden bg-gradient-to-br from-slate-100 to-slate-200 dark:from-gray-800 dark:to-gray-900 shadow-2xl flex items-center justify-center">
                  <SplineViewerEmbed />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Links Section */}
        <section className="py-16 relative">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Link href="/ai-assistant">
                <Card className="cosmic-card hover:space-glow transition-all h-full">
                  <CardContent className="p-6 text-center">
                    <div className="bg-blue-600/20 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                      <User className="h-8 w-8 text-blue-400" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-2">AI Assistant</h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      Chat with our AI to get instant answers about satellite data, weather patterns, and geospatial
                      insights.
                    </p>
                  </CardContent>
                </Card>
              </Link>
              <Link href="/api-integration">
                <Card className="cosmic-card hover:space-glow transition-all h-full">
                  <CardContent className="p-6 text-center">
                    <div className="bg-green-600/20 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                      <Globe className="h-8 w-8 text-green-400" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-2">API Integration</h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      Access our powerful geospatial API to integrate satellite data and analytics into your
                      applications.
                    </p>
                  </CardContent>
                </Card>
              </Link>
              <Link href="/dashboard">
                <Card className="cosmic-card hover:space-glow transition-all h-full">
                  <CardContent className="p-6 text-center">
                    <div className="bg-purple-600/20 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                      <BarChart3 className="h-8 w-8 text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-2">Live Dashboard</h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      Explore real-time geospatial intelligence with interactive visualizations and analytics.
                    </p>
                  </CardContent>
                </Card>
              </Link>
            </div>
          </div>
        </section>

        {/* Simple Info Section */}
        <section className="py-16 relative">
          <div className="container mx-auto px-4 text-center">
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              GeoVerse bridges human language with space-borne intelligence for better understanding of our planet.
            </p>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-8 sm:py-12 border-t border-white/30 dark:border-white/20 bg-space-gradient backdrop-blur-sm">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
              <div>
                <div className="flex items-center space-x-2 mb-4">
                  <Globe className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600 dark:text-blue-400" />
                  <span className="text-base sm:text-lg font-bold text-gray-800 dark:text-white">GeoVerse</span>
                </div>
                <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm sm:text-base">
                  Bridging human language with space-borne intelligence for a better understanding of our planet.
                </p>
                <div className="flex space-x-4">
                  <a
                    href="#"
                    className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  >
                    <Github className="h-4 w-4 sm:h-5 sm:w-5" />
                  </a>
                  <a
                    href="#"
                    className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  >
                    <Linkedin className="h-4 w-4 sm:h-5 sm:w-5" />
                  </a>
                  <a
                    href="#"
                    className="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  >
                    <Twitter className="h-4 w-4 sm:h-5 sm:w-5" />
                  </a>
                </div>
              </div>
              <div>
                <h3 className="text-gray-800 dark:text-white font-semibold mb-4">Contact Info</h3>
                <div className="space-y-2 text-gray-600 dark:text-gray-400 text-sm sm:text-base">
                  <p className="flex items-center">
                    <Mail className="h-3 w-3 sm:h-4 sm:w-4 mr-2" />
                    hello@geoverse.ai
                  </p>
                  <p className="flex items-center">
                    <MapPin className="h-3 w-3 sm:h-4 sm:w-4 mr-2" />
                    Bangalore, India
                  </p>
                </div>
              </div>
              <div>
                <h3 className="text-gray-800 dark:text-white font-semibold mb-4">Feedback</h3>
                <div className="space-y-3">
                  <Textarea
                    placeholder="Share your thoughts..."
                    className="bg-white/70 dark:bg-white/10 border-white/30 dark:border-white/20 text-gray-800 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400"
                  />
                  <Button className="w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600">
                    Send Feedback
                  </Button>
                </div>
              </div>
            </div>
            <div className="border-t border-white/30 dark:border-white/20 mt-6 sm:mt-8 pt-6 sm:pt-8 text-center">
              <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
                © 2025 Built by GeoVerse Team. All rights reserved.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import {
  Code2,
  Terminal,
  Key,
  Shield,
  CheckCircle,
  Copy,
  BookOpen,
  Download,
  Rocket,
  ArrowRight,
  CloudRain,
  TreePine,
  Map,
  Satellite,
} from "lucide-react"
import Navbar from "@/components/navbar"
import { useTheme } from "@/components/theme-provider"

// Enhanced Background Component
function EnhancedBackground({ isDark }: { isDark: boolean }) {
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
      <div className="nebula-clouds">
        <div className="nebula-cloud nebula-1" />
        <div className="nebula-cloud nebula-2" />
      </div>
    </div>
  )
}

export default function ApiIntegrationPage() {
  const { theme } = useTheme()
  const isDark = theme === "dark"

  const apiExamples = [
    {
      title: "Weather Data Query",
      language: "curl",
      code: `curl -X GET "https://api.geoverse.ai/v1/weather" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "location": "Delhi, India",
    "date": "2024-01-15",
    "parameters": ["temperature", "humidity", "rainfall"]
  }'`,
    },
    {
      title: "NDVI Analysis Request",
      language: "javascript",
      code: `const response = await fetch('https://api.geoverse.ai/v1/ndvi', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    coordinates: [77.2090, 28.6139],
    timeRange: {
      start: "2024-01-01",
      end: "2024-01-31"
    },
    resolution: "10m"
  })
});

const data = await response.json();`,
    },
    {
      title: "Satellite Image Search",
      language: "python",
      code: `import requests

url = "https://api.geoverse.ai/v1/satellite/search"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

payload = {
    "bbox": [77.0, 28.0, 78.0, 29.0],
    "date_range": ["2024-01-01", "2024-01-31"],
    "cloud_cover": {"max": 10},
    "satellite": "Sentinel-2"
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()`,
    },
  ]

  const useCases = [
    {
      icon: CloudRain,
      title: "Weather Monitoring",
      description: "Track real-time weather patterns, precipitation data, and climate analytics across regions.",
      features: ["Real-time weather data", "Historical climate analysis", "Precipitation forecasting"],
    },
    {
      icon: TreePine,
      title: "Agriculture Analytics",
      description: "Monitor crop health, vegetation indices, and agricultural land use changes over time.",
      features: ["NDVI monitoring", "Crop health assessment", "Yield prediction models"],
    },
    {
      icon: Map,
      title: "Urban Planning",
      description: "Analyze urban growth, land use changes, and infrastructure development patterns.",
      features: ["Land use classification", "Urban expansion tracking", "Infrastructure mapping"],
    },
    {
      icon: Satellite,
      title: "Disaster Management",
      description: "Monitor natural disasters, assess damage, and support emergency response planning.",
      features: ["Flood monitoring", "Wildfire detection", "Damage assessment"],
    },
  ]

  return (
    <div className={`min-h-screen relative ${isDark ? "bg-black" : "bg-white"}`}>
      {/* Background Image */}
      <div
        className="absolute inset-0 z-0 w-full h-full bg-center bg-cover opacity-20 pointer-events-none"
        style={{ backgroundImage: "url('/apikey1.jpg')" }}
        aria-hidden="true"
      />
      <Navbar />

      <EnhancedBackground isDark={isDark} />

      <main className="container mx-auto px-4 pt-24 pb-16">
        <div className="text-center mb-12 sm:mb-16 relative">
          {/* Background image only for heading section */}
          <div
            className="absolute inset-0 z-0 w-full h-full bg-center bg-cover opacity-20 pointer-events-none rounded-xl"
            style={{ backgroundImage: "url('/abcde.jpg')" }}
            aria-hidden="true"
          />
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-800 dark:text-white mb-4 relative z-10">
            <Code2 className="inline-block mr-3 h-8 w-8 text-green-600 dark:text-green-400" />
            GeoVerse API Integration
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto relative z-10">
            Developer-friendly geospatial intelligence API with comprehensive documentation and examples
          </p>
        </div>

        {/* API Key Section */}
        <div className="max-w-4xl mx-auto mb-16">
          <div className="relative rounded-2xl overflow-hidden">
            {/* Background image for the card */}
            <div
              className="absolute inset-0 w-full h-full bg-center bg-cover opacity-60 z-0"
              style={{ backgroundImage: "url('/abcde.jpg')" }}
              aria-hidden="true"
            />
            {/* Lighter dark overlay for better image visibility */}
            <div className="absolute inset-0 bg-gray-900/30 z-0" aria-hidden="true" />
            <Card className="bg-transparent border-green-200 dark:border-green-800/30 relative z-10 shadow-xl">
              <CardContent className="p-6 sm:p-8 text-center">
                <Key className="h-16 w-16 mx-auto mb-4 text-green-600 dark:text-green-400" />
                <h3 className="text-2xl font-bold text-gray-100 dark:text-white mb-4">Get Started with API Access</h3>
                <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
                  Get your free API key and start integrating GeoVerse's powerful geospatial intelligence into your
                  applications today.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <ApiKeyModal />
                  <Button
                    variant="outline"
                    size="lg"
                    className="border-green-200 dark:border-green-800 text-green-300 hover:bg-green-900/20 bg-transparent"
                  >
                    <BookOpen className="mr-2 h-5 w-5" />
                    View Documentation
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Code Examples */}
        <div className="mb-16 relative">
          {/* Background image only for code examples section */}
          <div
            className="absolute inset-0 z-0 w-full h-full bg-center bg-cover opacity-20 pointer-events-none rounded-xl"
            style={{ backgroundImage: "url('/abcde.jpg')" }}
            aria-hidden="true"
          />
          <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-8 text-center relative z-10">Code Examples</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 relative z-10">
            {apiExamples.map((example, index) => (
              <Card
                key={index}
                className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20 shadow-xl"
              >
                <CardHeader>
                  <CardTitle className="text-gray-800 dark:text-white flex items-center text-lg">
                    <Terminal className="mr-2 h-5 w-5 text-blue-600 dark:text-blue-400" />
                    {example.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative">
                    <pre className="bg-gray-900 dark:bg-gray-800 p-4 rounded-lg text-xs text-gray-100 overflow-x-auto max-h-64">
                      <code>{example.code}</code>
                    </pre>
                    <Button
                      size="sm"
                      variant="outline"
                      className="absolute top-2 right-2 bg-white/10 border-white/20 text-white hover:bg-white/20"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Use Cases */}
        <div>
          <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-8 text-center">Use Cases</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {useCases.map((useCase, index) => (
              <Card
                key={index}
                className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20 shadow-xl"
              >
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
                      <useCase.icon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">{useCase.title}</h4>
                      <p className="text-gray-600 dark:text-gray-300 mb-4">{useCase.description}</p>
                      <ul className="space-y-1">
                        {useCase.features.map((feature, idx) => (
                          <li key={idx} className="text-sm text-gray-500 dark:text-gray-400 flex items-center">
                            <ArrowRight className="h-3 w-3 mr-2 text-blue-500" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

// API Key Modal Component
function ApiKeyModal() {
  const [step, setStep] = useState(1)
  const [apiKey, setApiKey] = useState("")

  const generateApiKey = () => {
    const key = "gv_" + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
    setApiKey(key)
    setStep(2)
  }

  const copyApiKey = () => {
    navigator.clipboard.writeText(apiKey)
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          size="lg"
          className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg shadow-xl"
        >
          <Key className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
          Get API Key
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-white/20">
        <DialogHeader>
          <DialogTitle className="text-center text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
            Get Your API Key
          </DialogTitle>
        </DialogHeader>

        {step === 1 && (
          <div className="space-y-6 mt-6">
            <div className="text-center">
              <Shield className="h-16 w-16 mx-auto mb-4 text-green-500" />
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                Get instant access to GeoVerse API with your free developer key
              </p>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="dev-name">Developer Name</Label>
                <Input
                  id="dev-name"
                  placeholder="Your Name"
                  className="bg-white/70 dark:bg-white/10 border-white/30 dark:border-white/20"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dev-email">Email Address</Label>
                <Input
                  id="dev-email"
                  type="email"
                  placeholder="developer@example.com"
                  className="bg-white/70 dark:bg-white/10 border-white/30 dark:border-white/20"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-name">Project Name</Label>
                <Input
                  id="project-name"
                  placeholder="My GeoVerse Project"
                  className="bg-white/70 dark:bg-white/10 border-white/30 dark:border-white/20"
                />
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-800 dark:text-white mb-2">Free Tier Includes:</h4>
              <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  1,000 API calls per month
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Real-time satellite data access
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  Weather & NDVI analytics
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  24/7 developer support
                </li>
              </ul>
            </div>

            <Button onClick={generateApiKey} className="w-full bg-gradient-to-r from-green-500 to-blue-600">
              <Rocket className="mr-2 h-4 w-4" />
              Generate API Key
            </Button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6 mt-6">
            <div className="text-center">
              <CheckCircle className="h-16 w-16 mx-auto mb-4 text-green-500" />
              <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">API Key Generated!</h3>
              <p className="text-gray-600 dark:text-gray-300">Your API key is ready to use</p>
            </div>

            <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <code className="text-sm font-mono text-gray-800 dark:text-gray-200 break-all">{apiKey}</code>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={copyApiKey}
                  className="border-gray-300 dark:border-white/20 bg-transparent"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                <strong>Important:</strong> Save this API key securely. You won't be able to see it again.
              </p>
            </div>

            <div className="space-y-3">
              <Button className="w-full bg-blue-600 hover:bg-blue-700">
                <BookOpen className="mr-2 h-4 w-4" />
                View Documentation
              </Button>
              <Button variant="outline" className="w-full bg-transparent border-gray-300 dark:border-white/20">
                <Download className="mr-2 h-4 w-4" />
                Download SDK
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

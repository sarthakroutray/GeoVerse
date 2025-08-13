"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart3, Activity, CloudRain, TreePine, Satellite, Users, TrendingUp } from "lucide-react"
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts"
import Navbar from "@/components/navbar"
import { useTheme } from "@/components/theme-provider"

// Animated Counter Component
function AnimatedCounter({ end, duration = 2000, suffix = "" }: { end: number; duration?: number; suffix?: string }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTime: number
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      setCount(Math.floor(progress * end))
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [end, duration])

  return (
    <span>
      {count.toLocaleString()}
      {suffix}
    </span>
  )
}

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
        {[...Array(200)].map((_, i) => (
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

// Mock Data
const rainfallData = [
  { state: "Kerala", rainfall: 85, color: "#3b82f6" },
  { state: "Karnataka", rainfall: 65, color: "#06b6d4" },
  { state: "Tamil Nadu", rainfall: 45, color: "#8b5cf6" },
  { state: "Maharashtra", rainfall: 35, color: "#f59e0b" },
  { state: "Gujarat", rainfall: 25, color: "#ef4444" },
  { state: "Rajasthan", rainfall: 15, color: "#f97316" },
]

const vegetationData = [
  { month: "Jan", ndvi: 0.3, area: 45000 },
  { month: "Feb", ndvi: 0.35, area: 47000 },
  { month: "Mar", ndvi: 0.4, area: 52000 },
  { month: "Apr", ndvi: 0.55, area: 58000 },
  { month: "May", ndvi: 0.7, area: 65000 },
  { month: "Jun", ndvi: 0.8, area: 72000 },
  { month: "Jul", ndvi: 0.85, area: 78000 },
  { month: "Aug", ndvi: 0.82, area: 76000 },
  { month: "Sep", ndvi: 0.75, area: 70000 },
  { month: "Oct", ndvi: 0.6, area: 62000 },
  { month: "Nov", ndvi: 0.45, area: 55000 },
  { month: "Dec", ndvi: 0.35, area: 48000 },
]

const satelliteCoverage = [
  { name: "Sentinel-2", coverage: 78, color: "#3b82f6" },
  { name: "Landsat-8", coverage: 65, color: "#06b6d4" },
  { name: "MODIS", coverage: 92, color: "#10b981" },
  { name: "ISRO Satellites", coverage: 85, color: "#8b5cf6" },
]

const userQueries = [
  { query: "Weather Delhi", count: 1250, size: 24 },
  { query: "Rainfall Mumbai", count: 980, size: 20 },
  { query: "NDVI Analysis", count: 750, size: 18 },
  { query: "Satellite Images", count: 650, size: 16 },
  { query: "Crop Health", count: 580, size: 15 },
  { query: "Land Use", count: 420, size: 14 },
  { query: "Flood Monitoring", count: 380, size: 13 },
  { query: "Urban Growth", count: 320, size: 12 },
]

const liveStats = [
  { label: "Active Users", value: 12847, icon: Users, color: "text-blue-400" },
  { label: "API Calls Today", value: 89234, icon: Activity, color: "text-green-400" },
  { label: "Satellite Images", value: 5678, icon: Satellite, color: "text-purple-400" },
  { label: "Data Points", value: 234567, icon: BarChart3, color: "text-orange-400" },
]

export default function DashboardPage() {
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className={`min-h-screen ${isDark ? "bg-gray-900" : "bg-white"}`}>
      <Navbar />

      <EnhancedBackground isDark={isDark} />

      <main className="container mx-auto px-4 pt-24 pb-16">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-800 dark:text-white mb-4">
            <BarChart3 className="inline-block mr-3 h-8 w-8 text-purple-600 dark:text-purple-400" />
            Live GeoVerse Dashboard
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-2">
            Real-time geospatial intelligence across India
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Last updated: {currentTime.toLocaleTimeString()} IST
          </p>
        </div>

        {/* Live Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {liveStats.map((stat, index) => (
            <Card
              key={index}
              className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20"
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                    <p className={`text-2xl font-bold ${stat.color}`}>
                      <AnimatedCounter end={stat.value} />
                    </p>
                  </div>
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Rainfall Heatmap */}
          <Card className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20">
            <CardHeader>
              <CardTitle className="text-gray-800 dark:text-white flex items-center">
                <CloudRain className="mr-2 h-5 w-5 text-blue-600 dark:text-blue-400" />
                Rainfall Heatmap (mm)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  rainfall: {
                    label: "Rainfall",
                    color: "hsl(var(--chart-1))",
                  },
                }}
                className="h-[300px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={rainfallData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke={isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"}
                    />
                    <XAxis dataKey="state" stroke={isDark ? "#fff" : "#000"} fontSize={12} />
                    <YAxis stroke={isDark ? "#fff" : "#000"} fontSize={12} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="rainfall" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
              <div className="mt-4 grid grid-cols-3 gap-2">
                {rainfallData.slice(0, 6).map((item, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: item.color }} />
                    <span className="text-xs text-gray-600 dark:text-gray-300">{item.state}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Vegetation Index */}
          <Card className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20">
            <CardHeader>
              <CardTitle className="text-gray-800 dark:text-white flex items-center">
                <TreePine className="mr-2 h-5 w-5 text-green-600 dark:text-green-400" />
                Vegetation Index (NDVI)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  ndvi: {
                    label: "NDVI",
                    color: "hsl(var(--chart-2))",
                  },
                }}
                className="h-[300px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={vegetationData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke={isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"}
                    />
                    <XAxis dataKey="month" stroke={isDark ? "#fff" : "#000"} fontSize={12} />
                    <YAxis stroke={isDark ? "#fff" : "#000"} fontSize={12} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Area type="monotone" dataKey="ndvi" stroke="#10b981" fill="url(#colorNdvi)" strokeWidth={2} />
                    <defs>
                      <linearGradient id="colorNdvi" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
                      </linearGradient>
                    </defs>
                  </AreaChart>
                </ResponsiveContainer>
              </ChartContainer>
              <div className="mt-4 flex justify-between text-sm text-gray-600 dark:text-gray-300">
                <span>Peak Season: July</span>
                <span>Current NDVI: 0.75</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Second Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Satellite Coverage */}
          <Card className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20">
            <CardHeader>
              <CardTitle className="text-gray-800 dark:text-white flex items-center">
                <Satellite className="mr-2 h-5 w-5 text-purple-600 dark:text-purple-400" />
                Satellite Coverage Area
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {satelliteCoverage.map((satellite, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-300">{satellite.name}</span>
                      <span className="text-sm font-semibold text-gray-800 dark:text-white">{satellite.coverage}%</span>
                    </div>
                    <Progress value={satellite.coverage} className="h-2" />
                  </div>
                ))}
              </div>
              <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    <AnimatedCounter end={847} />
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Active Satellites</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    <AnimatedCounter end={92} suffix="%" />
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">India Coverage</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* User Queries Word Cloud */}
          <Card className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20">
            <CardHeader>
              <CardTitle className="text-gray-800 dark:text-white flex items-center">
                <TrendingUp className="mr-2 h-5 w-5 text-orange-600 dark:text-orange-400" />
                Popular User Queries
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-[280px] overflow-y-auto">
                {userQueries.map((query, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Badge
                        variant="secondary"
                        className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border-0"
                        style={{ fontSize: `${Math.max(query.size - 8, 10)}px` }}
                      >
                        {query.query}
                      </Badge>
                    </div>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      <AnimatedCounter end={query.count} />
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-white/10">
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-300">
                  <span>Total Queries Today:</span>
                  <span className="font-semibold">
                    <AnimatedCounter end={6358} />
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Real-time Activity Feed */}
        <Card className="bg-white/90 dark:bg-white/10 backdrop-blur-md border-white/30 dark:border-white/20">
          <CardHeader>
            <CardTitle className="text-gray-800 dark:text-white flex items-center">
              <Activity className="mr-2 h-5 w-5 text-green-600 dark:text-green-400" />
              Real-time Activity Feed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[200px] overflow-y-auto">
              {[
                { time: "2 sec ago", activity: "New satellite image processed for Mumbai region", type: "success" },
                { time: "15 sec ago", activity: "Weather data updated for Delhi NCR", type: "info" },
                { time: "32 sec ago", activity: "NDVI analysis completed for Punjab", type: "success" },
                { time: "1 min ago", activity: "API request from Agriculture Ministry", type: "warning" },
                { time: "2 min ago", activity: "Flood monitoring alert for Kerala", type: "error" },
                { time: "3 min ago", activity: "User query: 'Crop health in Karnataka'", type: "info" },
              ].map((item, index) => (
                <div key={index} className="flex items-start space-x-3 p-2 rounded-lg bg-gray-50 dark:bg-white/5">
                  <div
                    className={`w-2 h-2 rounded-full mt-2 ${
                      item.type === "success"
                        ? "bg-green-400"
                        : item.type === "error"
                          ? "bg-red-400"
                          : item.type === "warning"
                            ? "bg-yellow-400"
                            : "bg-blue-400"
                    }`}
                  />
                  <div className="flex-1">
                    <p className="text-sm text-gray-700 dark:text-gray-300">{item.activity}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

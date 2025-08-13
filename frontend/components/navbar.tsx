"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Menu, X, Sun, Moon } from "lucide-react"
import { useTheme } from "@/components/theme-provider"

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const { theme, setTheme } = useTheme()

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-[#2d0036] via-[#3a185a] to-[#1a0026] bg-opacity-90 backdrop-blur-md shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-end h-16">
          <Link href="/" className="flex items-center space-x-2 mr-auto">
            <span className="text-xl font-bold text-white drop-shadow">GeoVerse</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link
              href="/dashboard"
              className="text-white hover:text-cyan-300 transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/ai-assistant"
              className="text-white hover:text-cyan-300 transition-colors"
            >
              AI Assistant
            </Link>
            <Link
              href="/api-integration"
              className="text-white hover:text-cyan-300 transition-colors"
            >
              API
            </Link>
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="text-white hover:text-cyan-300"
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-2">
            <Button variant="ghost" size="sm" onClick={toggleTheme} className="text-white">
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              className="text-white"
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden py-4">
            <div className="flex flex-col space-y-3">
              <Link
                href="/dashboard"
                className="text-white hover:text-cyan-300 transition-colors px-2 py-1"
                onClick={() => setIsOpen(false)}
              >
                Dashboard
              </Link>
              <Link
                href="/ai-assistant"
                className="text-white hover:text-cyan-300 transition-colors px-2 py-1"
                onClick={() => setIsOpen(false)}
              >
                AI Assistant
              </Link>
              <Link
                href="/api-integration"
                className="text-white hover:text-cyan-300 transition-colors px-2 py-1"
                onClick={() => setIsOpen(false)}
              >
                API Integration
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

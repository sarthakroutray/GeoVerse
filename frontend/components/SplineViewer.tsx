"use client"

import { useEffect, useState } from "react"

declare global {
  namespace JSX {
    interface IntrinsicElements {
      "spline-viewer": React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
        url?: string
      }
    }
  }
}

export default function SplineViewer() {
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    const script = document.createElement("script")
    script.type = "module"
    script.src = "https://unpkg.com/@splinetool/viewer@1.10.22/build/spline-viewer.js"
    script.onload = () => setLoaded(true)
    document.body.appendChild(script)

    return () => {
      document.body.removeChild(script)
    }
  }, [])

  return loaded ? (
    <spline-viewer
      url="https://prod.spline.design/3UzGWg8BpdFpT4XG/scene.splinecode"
      style={{ width: "100%", height: "100%", background: "transparent" }}
    />
  ) : (
    <div className="text-center text-gray-600 dark:text-gray-300">Loading 3D Scene...</div>
  )
}

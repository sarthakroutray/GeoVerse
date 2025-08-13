"use client";

import dynamic from 'next/dynamic';
const Spline = dynamic(() => import('@splinetool/react-spline').then(mod => mod.default), { ssr: false });

export default function Page() {
  return (
    <div style={{ width: 600, height: 400 }}>
      <Spline scene="https://prod.spline.design/3UzGWg8BpdFpT4XG/scene.splinecode" />
    </div>
  );
}

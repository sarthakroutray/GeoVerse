import Spline from '@splinetool/react-spline/next';
import React from 'react';

interface SplineEarthProps {
  width?: string | number;
  height?: string | number;
  style?: React.CSSProperties;
}

const SplineEarth: React.FC<SplineEarthProps> = ({ width = '100%', height = 400, style }) => {
  return (
    <div style={{ width, height, ...style }}>
      <Spline scene="https://prod.spline.design/3UzGWg8BpdFpT4XG/scene.splinecode" />
    </div>
  );
};

export default SplineEarth;

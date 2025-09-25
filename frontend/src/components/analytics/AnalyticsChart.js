import { useState, useEffect, useRef } from 'react';

export default function AnalyticsChart({ 
  title, 
  data = [], 
  type = 'line', 
  color = 'blue',
  height = 300,
  showGrid = true,
  showTooltip = true 
}) {
  const canvasRef = useRef(null);
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (!data.length) return;
    drawChart();
  }, [data, type, color, height]);

  const drawChart = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    
    // Set canvas size
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    
    const width = rect.width;
    const height = rect.height;
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (!data.length) return;

    // Find min/max values
    const values = data.map(d => d.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const valueRange = maxValue - minValue || 1;

    // Draw grid
    if (showGrid) {
      ctx.strokeStyle = '#f3f4f6';
      ctx.lineWidth = 1;
      
      // Horizontal grid lines
      for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
      }
      
      // Vertical grid lines
      const stepX = chartWidth / (data.length - 1 || 1);
      for (let i = 0; i < data.length; i++) {
        const x = padding + stepX * i;
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, height - padding);
        ctx.stroke();
      }
    }

    // Draw chart based on type
    if (type === 'line') {
      drawLineChart(ctx, data, padding, chartWidth, chartHeight, minValue, valueRange, color);
    } else if (type === 'bar') {
      drawBarChart(ctx, data, padding, chartWidth, chartHeight, minValue, valueRange, color);
    } else if (type === 'area') {
      drawAreaChart(ctx, data, padding, chartWidth, chartHeight, minValue, valueRange, color);
    }

    // Draw axes labels
    drawAxes(ctx, data, padding, width, height, chartWidth, chartHeight, minValue, maxValue);
  };

  const drawLineChart = (ctx, data, padding, chartWidth, chartHeight, minValue, valueRange, color) => {
    const stepX = chartWidth / (data.length - 1 || 1);
    
    ctx.strokeStyle = getColorValue(color, 500);
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    data.forEach((point, index) => {
      const x = padding + stepX * index;
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.stroke();

    // Draw points
    ctx.fillStyle = getColorValue(color, 600);
    data.forEach((point, index) => {
      const x = padding + stepX * index;
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
      
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  const drawBarChart = (ctx, data, padding, chartWidth, chartHeight, minValue, valueRange, color) => {
    const barWidth = chartWidth / data.length * 0.8;
    const barSpacing = chartWidth / data.length * 0.2;
    
    ctx.fillStyle = getColorValue(color, 500);
    
    data.forEach((point, index) => {
      const x = padding + (chartWidth / data.length) * index + barSpacing / 2;
      const barHeight = ((point.value - minValue) / valueRange) * chartHeight;
      const y = padding + chartHeight - barHeight;
      
      ctx.fillRect(x, y, barWidth, barHeight);
    });
  };

  const drawAreaChart = (ctx, data, padding, chartWidth, chartHeight, minValue, valueRange, color) => {
    const stepX = chartWidth / (data.length - 1 || 1);
    
    // Draw filled area
    ctx.fillStyle = getColorValue(color, 100);
    ctx.beginPath();
    ctx.moveTo(padding, padding + chartHeight);
    
    data.forEach((point, index) => {
      const x = padding + stepX * index;
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
      ctx.lineTo(x, y);
    });
    
    ctx.lineTo(padding + chartWidth, padding + chartHeight);
    ctx.closePath();
    ctx.fill();
    
    // Draw line on top
    drawLineChart(ctx, data, padding, chartWidth, chartHeight, minValue, valueRange, color);
  };

  const drawAxes = (ctx, data, padding, width, height, chartWidth, chartHeight, minValue, maxValue) => {
    ctx.fillStyle = '#6b7280';
    ctx.font = '12px system-ui';
    ctx.textAlign = 'center';
    
    // X-axis labels (dates)
    const stepX = chartWidth / (data.length - 1 || 1);
    data.forEach((point, index) => {
      if (index % Math.ceil(data.length / 6) === 0) { // Show every 6th label
        const x = padding + stepX * index;
        const date = new Date(point.date);
        const label = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        ctx.fillText(label, x, height - 10);
      }
    });
    
    // Y-axis labels (values)
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
      const value = minValue + (maxValue - minValue) * (1 - i / 5);
      const y = padding + (chartHeight / 5) * i;
      ctx.fillText(formatValue(value), padding - 10, y + 4);
    }
  };

  const formatValue = (value) => {
    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K';
    } else {
      return Math.round(value).toString();
    }
  };

  const getColorValue = (color, shade) => {
    const colors = {
      blue: { 100: '#dbeafe', 500: '#3b82f6', 600: '#2563eb' },
      green: { 100: '#dcfce7', 500: '#22c55e', 600: '#16a34a' },
      purple: { 100: '#f3e8ff', 500: '#a855f7', 600: '#9333ea' },
      yellow: { 100: '#fef3c7', 500: '#eab308', 600: '#ca8a04' },
      red: { 100: '#fee2e2', 500: '#ef4444', 600: '#dc2626' },
    };
    return colors[color]?.[shade] || colors.blue[shade];
  };

  const handleMouseMove = (e) => {
    if (!data.length) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setMousePos({ x: e.clientX, y: e.clientY });
    
    // Find closest data point
    const padding = 40;
    const chartWidth = rect.width - padding * 2;
    const stepX = chartWidth / (data.length - 1 || 1);
    
    let closestIndex = -1;
    let closestDistance = Infinity;
    
    data.forEach((point, index) => {
      const pointX = padding + stepX * index;
      const distance = Math.abs(x - pointX);
      
      if (distance < closestDistance && distance < 20) {
        closestDistance = distance;
        closestIndex = index;
      }
    });
    
    if (closestIndex >= 0) {
      setHoveredPoint(data[closestIndex]);
    } else {
      setHoveredPoint(null);
    }
  };

  const handleMouseLeave = () => {
    setHoveredPoint(null);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div className="relative">
        <canvas
          ref={canvasRef}
          className="w-full cursor-crosshair"
          style={{ height: `${height}px` }}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        />
        
        {/* Tooltip */}
        {showTooltip && hoveredPoint && (
          <div
            className="absolute z-10 bg-gray-900 text-white text-sm rounded px-2 py-1 pointer-events-none"
            style={{
              left: mousePos.x - 100,
              top: mousePos.y - 60,
            }}
          >
            <div className="font-medium">{formatValue(hoveredPoint.value)}</div>
            <div className="text-gray-300">
              {new Date(hoveredPoint.date).toLocaleDateString()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

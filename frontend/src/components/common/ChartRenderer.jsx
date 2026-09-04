import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
} from 'chart.js';
import { Bar, Doughnut, Pie, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
);

export const ChartRenderer = ({
  type = 'bar',
  labels = [],
  data = [],
  title = '',
  height = 260,
  horizontal = false
}) => {
  const palette = [
    '#38BDF8', // Cyan/Sky
    '#34D399', // Emerald
    '#FBBF24', // Amber
    '#F472B6', // Pink
    '#A78BFA', // Purple
    '#60A5FA', // Blue
    '#FB7185', // Rose
    '#2DD4BF', // Teal
  ];

  const backgroundColors = labels.map((_, i) => palette[i % palette.length]);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Responses',
        data,
        backgroundColor: type === 'doughnut' || type === 'pie' ? backgroundColors : 'rgba(56, 189, 248, 0.85)',
        borderColor: type === 'doughnut' || type === 'pie' ? '#FFFFFF' : '#0284C7',
        borderWidth: type === 'doughnut' || type === 'pie' ? 3 : 1.5,
        borderRadius: type === 'bar' ? 6 : 0,
        hoverBackgroundColor: '#0EA5E9',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontal ? 'y' : 'x',
    plugins: {
      legend: {
        display: type === 'doughnut' || type === 'pie',
        position: 'bottom',
        labels: {
          color: '#24110A',
          font: { family: 'Inter', size: 12, weight: 'bold' },
          padding: 14,
          usePointStyle: true
        }
      },
      title: {
        display: !!title,
        text: title,
        color: '#24110A',
        font: { family: 'Inter', size: 14, weight: 'bold' },
        padding: { bottom: 12 }
      },
      tooltip: {
        backgroundColor: '#FFFFFF',
        titleColor: '#24110A',
        bodyColor: '#EA580C',
        borderColor: '#FAD5C0',
        borderWidth: 1.5,
        padding: 12,
        cornerRadius: 10,
        boxShadow: '0 4px 15px rgba(249, 115, 66, 0.15)'
      }
    },
    scales: type === 'bar' || type === 'line' ? {
      x: {
        grid: { color: 'rgba(250, 213, 192, 0.4)' },
        ticks: { color: '#3B1F14', font: { family: 'Inter', size: 11, weight: 'bold' } }
      },
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(250, 213, 192, 0.4)' },
        ticks: { color: '#3B1F14', font: { family: 'Inter', size: 11, weight: 'bold' } }
      }
    } : {}
  };

  return (
    <div style={{ height: `${height}px` }} className="w-full relative">
      {type === 'bar' && <Bar data={chartData} options={options} />}
      {type === 'doughnut' && <Doughnut data={chartData} options={options} />}
      {type === 'pie' && <Pie data={chartData} options={options} />}
      {type === 'line' && <Line data={chartData} options={options} />}
    </div>
  );
};

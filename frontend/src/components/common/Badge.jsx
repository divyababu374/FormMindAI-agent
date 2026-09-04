import React from 'react';

export const Badge = ({ children, variant = 'peach', className = '' }) => {
  const variants = {
    blue: 'bg-sky-50 text-sky-800 border-sky-300 font-semibold',
    green: 'bg-emerald-50 text-emerald-800 border-emerald-300 font-semibold',
    purple: 'bg-purple-50 text-purple-800 border-purple-300 font-semibold',
    amber: 'bg-amber-50 text-amber-900 border-amber-300 font-semibold',
    rose: 'bg-rose-50 text-rose-800 border-rose-300 font-semibold',
    peach: 'bg-orange-50 text-orange-900 border-orange-300 font-semibold',
    slate: 'bg-[#FFF2EB] text-[#3B1F14] border-[#FAD5C0] font-semibold'
  };

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs border ${variants[variant] || variants.peach} ${className}`}>
      {children}
    </span>
  );
};

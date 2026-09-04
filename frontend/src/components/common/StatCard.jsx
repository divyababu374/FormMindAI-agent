import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'peach', trend }) => {
  const colorMap = {
    blue: {
      bg: 'bg-sky-50',
      border: 'border-sky-200',
      text: 'text-sky-700',
      glow: 'group-hover:border-sky-400'
    },
    emerald: {
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      text: 'text-emerald-700',
      glow: 'group-hover:border-emerald-400'
    },
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-700',
      glow: 'group-hover:border-purple-400'
    },
    amber: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-800',
      glow: 'group-hover:border-amber-400'
    },
    peach: {
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      text: 'text-brand-600',
      glow: 'group-hover:border-brand-400'
    }
  };

  const scheme = colorMap[color] || colorMap.peach;

  return (
    <div className="group relative p-5 rounded-2xl bg-white border border-[#FAD5C0] shadow-sm hover:shadow-md hover:border-brand-400 transition-all duration-300 overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-bold text-[#7A4533] uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-[#24110A] mt-2 tracking-tight">{value}</h3>
          {subtitle && <p className="text-xs text-[#6B3B2B] mt-1 font-medium">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${scheme.bg} ${scheme.text} border ${scheme.border} shadow-sm`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-4 pt-3 border-t border-[#FDE4D7] flex items-center gap-1.5 text-xs text-emerald-700 font-semibold">
          <span>{trend}</span>
        </div>
      )}
    </div>
  );
};

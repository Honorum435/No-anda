import React from "react";

export default function CTA() {
  return (
    <section className="bg-[#1B7C6A] py-20 relative overflow-hidden">
      {/* Patrón de ondas de fondo */}
      <div className="absolute inset-0 opacity-20">
        <svg className="w-full h-full" viewBox="0 0 1200 200" fill="none">
          <path d="M0,100 Q300,50 600,100 T1200,100 L1200,200 L0,200 Z" fill="#3D8C80"/>
          <path d="M0,150 Q300,100 600,150 T1200,150 L1200,200 L0,200 Z" fill="#2A6B5F"/>
        </svg>
      </div>
      
      <div className="max-w-6xl mx-auto px-24 flex items-center justify-between relative z-10">
        <div className="flex-1">
          <h2 className="text-5xl font-bold text-white leading-tight" style={{fontFamily:'Georgia,serif'}}>
            Let's Help Other With<br />
            <span className="text-6xl">Your Charity</span>
          </h2>
        </div>
        
        <div className="flex-1 flex justify-end">
          <button className="bg-[#FFE9A7] text-[#23423D] px-8 py-4 rounded-lg font-semibold text-lg shadow-lg hover:bg-[#FFD54F] transition transform hover:scale-105">
            Donate Now
          </button>
        </div>
      </div>
    </section>
  );
}

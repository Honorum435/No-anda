import React from "react";

export default function Stats() {
  return (
    <section className="bg-[#1B7C6A] py-20 flex flex-row justify-center items-center text-white relative overflow-hidden">
      {/* Fondo decorativo con logos difuminados */}
      <div className="absolute inset-0 opacity-[0.07] pointer-events-none select-none">
        <div className="w-full h-full flex flex-wrap justify-around items-center gap-16 p-10">
          <img src="/img/Logo1.png" alt="bg logo" className="h-40 object-contain" />
          <img src="/img/Logo2.png" alt="bg logo" className="h-40 object-contain" />
          <img src="/img/logo3.png" alt="bg logo" className="h-40 object-contain" />
          <img src="/img/Logo4.png" alt="bg logo" className="h-40 object-contain" />
          <img src="/img/Logo1.png" alt="bg logo" className="h-40 object-contain" />
          <img src="/img/Logo2.png" alt="bg logo" className="h-40 object-contain" />
          <img src="/img/logo3.png" alt="bg logo" className="h-40 object-contain" />
          <img src="/img/Logo4.png" alt="bg logo" className="h-40 object-contain" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-[#1B7C6A]/60 via-[#1B7C6A]/70 to-[#1B7C6A]" />
      </div>
      
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-12 w-full max-w-6xl mx-auto relative z-10">
        {/* Stat 1 */}
        <div className="flex items-center gap-4">
          <img src="/img/Logo1.png" alt="Logo 1" className="w-16 h-16 object-contain bg-white/10 p-2 rounded" />
          <div className="text-left">
            <div className="text-4xl font-bold leading-tight">985+</div>
            <div className="text-sm opacity-80 mt-1">Donation Received</div>
          </div>
        </div>
        {/* Stat 2 */}
        <div className="flex items-center gap-4">
          <img src="/img/Logo2.png" alt="Logo 2" className="w-16 h-16 object-contain bg-white/10 p-2 rounded" />
          <div className="text-left">
            <div className="text-4xl font-bold leading-tight">$10 M</div>
            <div className="text-sm opacity-80 mt-1">Money Donated</div>
          </div>
        </div>
        {/* Stat 3 */}
        <div className="flex items-center gap-4">
          <img src="/img/logo3.png" alt="Logo 3" className="w-16 h-16 object-contain bg-white/10 p-2 rounded" />
          <div className="text-left">
            <div className="text-4xl font-bold leading-tight">12+</div>
            <div className="text-sm opacity-80 mt-1">Active Campaigns</div>
          </div>
        </div>
        {/* Stat 4 */}
        <div className="flex items-center gap-4">
          <img src="/img/Logo4.png" alt="Logo 4" className="w-16 h-16 object-contain bg-white/10 p-2 rounded" />
          <div className="text-left">
            <div className="text-4xl font-bold leading-tight">$60 M</div>
            <div className="text-sm opacity-80 mt-1">Charity in last Year</div>
          </div>
        </div>
      </div>
    </section>
  );
}

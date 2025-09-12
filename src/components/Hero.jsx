import React from "react";

// Hero con parte izquierda crema y parte derecha amarilla
export default function Hero() {
  return (
    <section className="w-full">
      <div className="grid lg:grid-cols-2 min-h-[720px] lg:min-h-[820px]">
        {/* Izquierda (crema) */}
        <div className="bg-[#F7F3EB] px-8 lg:pl-24 lg:pr-16 py-20 flex flex-col justify-center">
          <h1 className="text-5xl lg:text-6xl font-serif text-[#23423D] leading-tight mb-10">
            Charity Is An Act Of A Soft Heart.
          </h1>
          <p className="text-[#23423D] text-lg leading-relaxed max-w-md mb-12">
            We've spent the last 5 years helping over 25,00000 teams just like yourself create and sustain successful online support.
          </p>
          <div className="flex items-center gap-6 flex-wrap mb-10">
            <button className="bg-[#1B7C6A] hover:bg-[#145C4E] text-white px-10 py-5 text-lg font-semibold rounded-md transition-colors shadow-sm">
              Donate Now
            </button>
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-18 h-18 w-16 h-16 rounded-full bg-[#FFE9A7] flex items-center justify-center">
                  <svg className="w-7 h-7 text-[#23423D] ml-1" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
                </div>
                <div className="absolute -inset-4 border-2 border-dashed border-[#1B7C6A] rounded-full animate-spin-slow"></div>
              </div>
              <span className="text-[#23423D] text-sm">Learn about us through video</span>
            </div>
          </div>
          <div className="flex items-center gap-10">
            <a href="#" className="text-[#23423D] hover:underline font-medium">Youtube</a>
            <a href="#" className="text-[#23423D] hover:underline font-medium">Facebook</a>
            <a href="#" className="text-[#23423D] hover:underline font-medium">Instagram</a>
          </div>
        </div>
        {/* Derecha (amarilla con imagen) */}
        <div className="relative bg-[#FFE9A7] flex items-end justify-center pl-8 pr-12 lg:pr-32 pb-0 pt-24 overflow-hidden">
          {/* Círculo decorativo atrás */}
          <div className="absolute -top-40 -right-40 w-[620px] h-[620px] bg-[#F7F3EB] rounded-full opacity-40 blur-3xl" aria-hidden="true" />
          <div className="relative w-[600px] h-[720px] md:w-[660px] md:h-[780px] lg:w-[720px] lg:h-[840px] flex items-end justify-center transition-all">
            <img
              src="/img/Recorte.png"
              alt="Charity Hero"
              className="w-full h-full object-contain select-none drop-shadow-2xl"
              draggable="false"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

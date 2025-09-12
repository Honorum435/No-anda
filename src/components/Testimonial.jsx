import React from "react";

export default function Testimonial() {
  return (
    <section className="px-24 py-24 bg-[#F7F3EB] flex flex-row items-center justify-center">
      <div className="max-w-6xl mx-auto flex items-center">
        {/* Imagen circular con fondo amarillo */}
        <div className="relative mr-16">
          <div className="w-80 h-80 bg-[#FFE9A7] rounded-full flex items-center justify-center overflow-hidden relative">
            <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80" alt="Mustafa Kamal" className="w-64 h-64 rounded-full object-cover" />
            
            {/* Badge de calificación */}
            <div className="absolute top-4 left-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              5.0
            </div>
          </div>
        </div>

        {/* Contenido del testimonial */}
        <div className="max-w-2xl">
          <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
            <p className="text-xl text-[#23423D] leading-relaxed">"We're very happy that the challenge went well, and we're grateful that we have a partner in Charity Challenge whom we could trust to take the best possible care of our supporters."</p>
          </div>
          
          <div className="ml-4">
            <div className="font-bold text-2xl text-[#23423D] mb-1">Mustafa Kamal</div>
            <div className="text-gray-500 text-lg">CEO, Toogle</div>
          </div>
        </div>

        {/* Controles de navegación */}
        <div className="ml-8 flex flex-col gap-4">
          <button className="w-12 h-12 rounded-full border-2 border-[#23423D] flex items-center justify-center hover:bg-[#23423D] hover:text-white transition">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button className="w-12 h-12 rounded-full bg-[#FFE9A7] flex items-center justify-center hover:bg-[#FFD54F] transition">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </section>
  );
}

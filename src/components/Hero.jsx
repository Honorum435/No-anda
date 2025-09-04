import React from "react";

export default function Hero() {
  return (
    <section className="w-full flex min-h-[600px]">
      {/* Columna izquierda: fondo crema */}
      <div className="w-1/2 bg-[#F7F3EB] flex flex-col justify-center pl-24 pr-8 py-24">
        <h1 className="text-6xl font-bold mb-8 text-[#23423D] leading-tight" style={{fontFamily:'Georgia,serif'}}>Charity Is An Act Of A Soft Heart.</h1>
        <p className="mb-8 text-xl text-[#23423D] max-w-md">We've spent the last 5 years helping over 250,000 teams just like yourself create and sustain successful online support.</p>
        <button className="bg-[#1B7C6A] text-white px-8 py-4 rounded font-semibold text-lg shadow hover:bg-[#145C4E] transition mb-8 w-48">Donate Now</button>
        <div className="flex space-x-8 text-[#23423D] text-lg font-medium">
          <a href="#" className="hover:underline">Youtube</a>
          <a href="#" className="hover:underline">Facebook</a>
          <a href="#" className="hover:underline">Instagram</a>
        </div>
      </div>
      {/* Columna derecha: fondo amarillo con imagen y botón */}
  <div className="w-1/2 bg-[#FFE9A7] flex items-center justify-center relative overflow-hidden">
        <img src="https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80" alt="Charity" className="object-cover h-full w-full" />
  {/* Eliminar el botón Donate Now del lado derecho */}
      </div>
    </section>
  );
}

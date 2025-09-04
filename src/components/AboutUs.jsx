import React from "react";

export default function AboutUs() {
  return (
    <section id="about" className="px-24 py-24 bg-[#F7F3EB] flex justify-center items-center">
      <div className="bg-white rounded-lg shadow-lg px-0 py-0 flex items-center max-w-4xl w-full relative">
        {/* Imagen semicírculo grande sobresaliendo */}
        <div className="absolute -left-32 top-1/2 -translate-y-1/2 z-10 w-[440px] h-[440px] overflow-hidden bg-white flex items-center justify-center shadow-xl">
          <img src="https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=600&q=80" alt="About Us" className="w-full h-full object-cover rounded-l-full" />
        </div>
        {/* Contenido a la derecha */}
        <div className="ml-[340px] px-12 py-14">
          <h2 className="text-5xl font-bold mb-6 text-[#23423D]" style={{fontFamily:'Georgia,serif'}}>About Us</h2>
          <p className="mb-6 text-lg text-[#23423D]">The legal definition of a charitable organization (and of charity) varies between countries and in some instances regions of the country. The regulation, the tax treatment, and the way in which charity law effects charitable organizations also vary.</p>
          <a href="#" className="text-[#23423D] font-semibold hover:underline">Read More</a>
        </div>
      </div>
    </section>
  );
}

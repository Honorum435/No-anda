import React from "react";

export default function Testimonial() {
  return (
    <section className="px-24 py-24 bg-[#F7F3EB] flex flex-row items-center justify-center">
      <div className="w-80 h-80 bg-yellow-200 rounded-full flex items-center justify-center overflow-hidden mr-16">
        <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="Testimonial" className="w-48 h-48 rounded-full object-cover" />
      </div>
      <div className="max-w-2xl">
        <div className="text-yellow-600 font-bold mb-2 text-lg">★ 5.0</div>
        <p className="text-2xl mb-6 text-[#23423D]">"We're very happy that the challenge went well, and we're grateful that we have a partner in Charity Challenge whom we could trust to take the best possible care of our supporters."</p>
        <div className="font-bold text-xl text-[#23423D]">Mustafa Kamal</div>
        <div className="text-gray-500">CEO, Toogle</div>
      </div>
    </section>
  );
}

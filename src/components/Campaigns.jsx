import React from "react";

const campaigns = [
  { title: "Covid - 19", img: "https://images.unsplash.com/photo-1588776814546-ec7e8c7e8c7e?auto=format&fit=crop&w=400&q=80" },
  { title: "Food Bank", img: "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?auto=format&fit=crop&w=400&q=80" },
  { title: "Safe Water", img: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80" },
];

export default function Campaigns() {
  return (
  <section className="px-24 py-24 bg-[#F7F3EB]">
      <h2 className="text-5xl font-bold mb-6 text-[#23423D]" style={{fontFamily:'Georgia,serif'}}>Support Your Community</h2>
      <p className="mb-10 text-lg text-[#23423D]">The legal definition of a charitable organization (and of charity) varies between countries and in charity law affects charitable organizations also vary.</p>
  <div className="grid grid-cols-3 gap-12 mb-8">
        {campaigns.map((c) => (
          <div key={c.title} className="bg-white rounded-lg shadow p-0 overflow-hidden">
            <img src={c.img} alt={c.title} className="w-full h-56 object-cover" />
            <div className="mt-2 font-semibold text-xl px-4 py-4">{c.title}</div>
          </div>
        ))}
      </div>
      <a href="#" className="text-[#23423D] font-semibold hover:underline">View All Campaign</a>
    </section>
  );
}

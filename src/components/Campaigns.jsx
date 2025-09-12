import React from "react";

const campaigns = [
  { 
    title: "Covid - 19", 
    img: "/img/covid 19.png"
  },
  { 
    title: "Food Bank", 
    img: "/img/Food bank.png"
  },
  { 
    title: "Safe Water", 
    img: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80"
  },
];

export default function Campaigns() {
  return (
    <section className="px-24 py-24 bg-[#F7F3EB]" style={{border: 'none', borderTop: 'none'}}>
      <div className="max-w-6xl mx-auto">
        <h2 className="text-5xl font-bold mb-6 text-[#23423D]" style={{fontFamily:'Georgia,serif'}}>Support Your Community</h2>
        <div className="w-16 h-1 bg-[#23423D] mb-6"></div>
        <p className="mb-10 text-lg text-[#23423D] max-w-2xl">The legal definition of a charitable organization (and of charity) varies between countries and in charity law affects charitable organizations also vary.</p>
        
        <div className="grid grid-cols-3 gap-12 mb-8">
          {campaigns.map((c) => (
            <div key={c.title} className="bg-white rounded-2xl shadow-lg flex flex-col items-center overflow-hidden">
              <div className="w-full aspect-[4/3] flex items-center justify-center overflow-hidden rounded-t-2xl bg-gray-100">
                <img src={c.img} alt={c.title} className="object-cover w-full h-full" />
              </div>
              <div className="font-semibold text-xl px-4 py-6 w-full text-center text-[#23423D]">{c.title}</div>
            </div>
          ))}
        </div>
        <div className="text-right">
          <a href="#" className="text-[#23423D] font-semibold hover:underline text-lg">View All Campaign</a>
        </div>
      </div>
    </section>
  );
}

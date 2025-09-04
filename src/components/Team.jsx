import React from "react";

const team = [
  { name: "Lily Gomez", role: "Founder", img: "https://randomuser.me/api/portraits/women/44.jpg", color: "bg-yellow-200" },
  { name: "Dm Lincoln", role: "Co-Founder", img: "https://randomuser.me/api/portraits/men/45.jpg", color: "bg-[#1B7C6A]" },
  { name: "Serena Mei", role: "Manager", img: "https://randomuser.me/api/portraits/women/46.jpg", color: "bg-yellow-200" },
  { name: "Abdel Latif", role: "Superviser", img: "https://randomuser.me/api/portraits/men/47.jpg", color: "bg-[#1B7C6A]" },
];

export default function Team() {
  return (
  <section className="px-24 py-24 bg-[#F7F3EB]">
      <h2 className="text-5xl font-bold mb-12 text-[#23423D] text-center" style={{fontFamily:'Georgia,serif'}}>Our Team</h2>
  <div className="grid grid-cols-4 gap-12">
        {team.map((member, idx) => (
          <div key={member.name} className="bg-white rounded-lg shadow p-6 flex flex-col items-center relative">
            <div className={`absolute -top-8 left-1/2 -translate-x-1/2 w-20 h-20 rounded-full ${member.color} flex items-center justify-center`}>
              <img src={member.img} alt={member.name} className="w-16 h-16 rounded-full object-cover" />
            </div>
            <div className="mt-16 font-semibold text-xl text-[#23423D]">{member.name}</div>
            <div className="text-gray-500">{member.role}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

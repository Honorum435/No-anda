import React from "react";

const team = [
  { 
    name: "Lily Gomez", 
    role: "Founder", 
    img: "https://images.unsplash.com/photo-1494790108755-2616b612b786?auto=format&fit=crop&w=300&q=80",
    accent1: "bg-yellow-300",
    accent2: "bg-green-200"
  },
  { 
    name: "Dm Lincoln", 
    role: "Co-Founder", 
    img: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&q=80",
    accent1: "bg-[#1B7C6A]",
    accent2: "bg-green-200"
  },
  { 
    name: "Serena Mei", 
    role: "Manager", 
    img: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=300&q=80",
    accent1: "bg-yellow-300",
    accent2: "bg-green-200"
  },
  { 
    name: "Abdel Latif", 
    role: "Superviser", 
    img: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
    accent1: "bg-[#1B7C6A]",
    accent2: "bg-green-200"
  },
];

export default function Team() {
  return (
    <section className="px-24 py-24 bg-[#F7F3EB]">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-5xl font-bold mb-6 text-[#23423D] text-center" style={{fontFamily:'Georgia,serif'}}>Our Team</h2>
        <div className="w-16 h-1 bg-[#23423D] mx-auto mb-12"></div>
        
        <div className="grid grid-cols-4 gap-8">
          {team.map((member, idx) => (
            <div key={member.name} className="flex flex-col items-center">
              <div className="relative mb-6">
                <div className="w-32 h-32 rounded-full overflow-hidden relative">
                  <img src={member.img} alt={member.name} className="w-full h-full object-cover" />
                  
                  {/* Accent semicircles */}
                  <div className={`absolute -top-2 -right-2 w-8 h-8 ${member.accent1} rounded-full`}></div>
                  <div className={`absolute -bottom-2 -left-2 w-8 h-8 ${member.accent2} rounded-full`}></div>
                </div>
              </div>
              
              <h3 className="font-semibold text-xl text-[#23423D] mb-1">{member.name}</h3>
              <p className="text-gray-500 text-sm">{member.role}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

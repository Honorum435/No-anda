import React from "react";

export default function Stats() {
  return (
    <section className="bg-[#1B7C6A] py-20 flex flex-row justify-center items-center text-white">
      <div className="flex flex-row gap-24 w-full max-w-6xl mx-auto">
        <div className="flex-1 text-center">
          <div className="text-4xl font-bold mb-2">985+</div>
          <div className="text-lg opacity-80">Donation Received</div>
        </div>
        <div className="flex-1 text-center">
          <div className="text-4xl font-bold mb-2">$10 M</div>
          <div className="text-lg opacity-80">Money Donated</div>
        </div>
        <div className="flex-1 text-center">
          <div className="text-4xl font-bold mb-2">12+</div>
          <div className="text-lg opacity-80">Active Campaigns</div>
        </div>
        <div className="flex-1 text-center">
          <div className="text-4xl font-bold mb-2">$60 M</div>
          <div className="text-lg opacity-80">Charity in last Year</div>
        </div>
      </div>
    </section>
  );
}

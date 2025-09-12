import React from "react";

export default function Footer() {
  return (
    <footer className="bg-[#F7F3EB] px-24 py-20">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-4 gap-12 mb-12">
          {/* Newsletter */}
          <div className="col-span-1">
            <h3 className="font-bold text-lg mb-4 text-[#23423D]">Newsletter</h3>
            <p className="mb-6 text-[#23423D] text-sm leading-relaxed">Subscribe to our newsletter to get more informations</p>
            <form className="flex">
              <input 
                type="email" 
                placeholder="Email" 
                className="flex-1 px-4 py-3 rounded-l bg-white text-[#23423D] border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#1B7C6A] focus:border-transparent" 
              />
              <button className="bg-[#1B7C6A] text-white px-6 py-3 rounded-r font-semibold hover:bg-[#145C4E] transition">
                Subscribe
              </button>
            </form>
          </div>

          {/* Navigation */}
          <div className="col-span-1">
            <h3 className="font-bold text-lg mb-4 text-[#23423D]">Navigation</h3>
            <ul className="space-y-2 text-[#23423D]">
              <li><a href="#" className="hover:underline text-sm">Home</a></li>
              <li><a href="#" className="hover:underline text-sm">Campaign</a></li>
              <li><a href="#" className="hover:underline text-sm">Team</a></li>
            </ul>
          </div>

          {/* About Us */}
          <div className="col-span-1">
            <h3 className="font-bold text-lg mb-4 text-[#23423D]">About Us</h3>
            <ul className="space-y-2 text-[#23423D]">
              <li><a href="#" className="hover:underline text-sm">About Us</a></li>
              <li><a href="#" className="hover:underline text-sm">Contact</a></li>
              <li><a href="#" className="hover:underline text-sm">Address</a></li>
            </ul>
          </div>

          {/* Help */}
          <div className="col-span-1">
            <h3 className="font-bold text-lg mb-4 text-[#23423D]">Help</h3>
            <ul className="space-y-2 text-[#23423D]">
              <li><a href="#" className="hover:underline text-sm">Donar Guide</a></li>
              <li><a href="#" className="hover:underline text-sm">FAQ</a></li>
              <li><a href="#" className="hover:underline text-sm">We Are Hiring</a></li>
              <li><a href="#" className="hover:underline text-sm">Returns</a></li>
            </ul>
          </div>
        </div>

        {/* Línea separadora */}
        <div className="border-t border-gray-300 pt-6">
          <div className="flex justify-between items-center text-sm text-[#23423D] opacity-70">
            <div>Designed By Tanim Khan</div>
            <div>WWW.Dribbble.Com/Tanim_ui</div>
          </div>
        </div>
      </div>
    </footer>
  );
}

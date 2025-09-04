import React from "react";

export default function Footer() {
  return (
    <footer className="bg-[#F7F3EB] px-24 py-20 border-t border-[#E5D9C5]">
      <div className="flex flex-row justify-between items-start mb-12">
        <div className="max-w-xs mr-24">
          <h3 className="font-bold text-lg mb-2 text-[#23423D]">Newsletter</h3>
          <p className="mb-4 text-[#23423D]">Subscribe to our newsletter to get more informations</p>
          <form className="flex">
            <input type="email" placeholder="Email" className="px-4 py-2 rounded-l bg-white text-[#23423D] border border-[#E5D9C5] focus:outline-none" />
            <button className="bg-[#1B7C6A] text-white px-4 py-2 rounded-r font-semibold">Subscribe</button>
          </form>
        </div>
        <div className="flex flex-col md:flex-row gap-16">
          <div>
            <h3 className="font-bold text-lg mb-2 text-[#23423D]">Navigation</h3>
            <ul className="text-[#23423D]">
              <li><a href="#" className="hover:underline">Home</a></li>
              <li><a href="#" className="hover:underline">Campaign</a></li>
              <li><a href="#" className="hover:underline">Team</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-2 text-[#23423D]">About Us</h3>
            <ul className="text-[#23423D]">
              <li><a href="#" className="hover:underline">About Us</a></li>
              <li><a href="#" className="hover:underline">Contact</a></li>
              <li><a href="#" className="hover:underline">Address</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-2 text-[#23423D]">Help</h3>
            <ul className="text-[#23423D]">
              <li><a href="#" className="hover:underline">Donor Guide</a></li>
              <li><a href="#" className="hover:underline">FAQ</a></li>
              <li><a href="#" className="hover:underline">We Are Hiring</a></li>
              <li><a href="#" className="hover:underline">Returns</a></li>
            </ul>
          </div>
        </div>
      </div>
      <div className="border-t border-[#E5D9C5] pt-4 text-center text-sm text-[#23423D] opacity-70">
        Designed by Tanim Khan | www.dribbble.com/Tanim_ui
      </div>
    </footer>
  );
}

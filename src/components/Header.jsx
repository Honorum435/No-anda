import React from "react";

export default function Header() {
  return (
    <header className="w-full flex h-28 border-b border-[#E5D9C5]">
      {/* Lado izquierdo crema */}
      <div className="w-1/2 flex items-center px-24 bg-[#F7F3EB]">
        <div className="text-3xl font-bold tracking-wide text-[#23423D]">Ta</div>
      </div>
      {/* Lado derecho amarillo suave */}
      <div className="w-1/2 flex items-center justify-end px-24 bg-[#FFE9A7]">
        <nav className="flex items-center space-x-12 text-lg font-medium text-[#23423D]">
          <a href="#about" className="hover:underline">About Us</a>
          <span className="mx-2">•</span>
          <a href="#campaign" className="hover:underline">Campaign</a>
          <span className="mx-2">•</span>
          <a href="#contact" className="hover:underline">Contact Us</a>
        </nav>
      </div>
    </header>
  );
}

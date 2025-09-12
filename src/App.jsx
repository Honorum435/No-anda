
import Header from './components/Header';
import Hero from './components/Hero';
import Stats from './components/Stats';
import Campaigns from './components/Campaigns';
import AboutUs from './components/AboutUs';
import Team from './components/Team';
import Testimonial from './components/Testimonial';
import CTA from './components/CTA';
import Footer from './components/Footer';

function App() {
  return (
    <div className="font-sans bg-[#F7F3EB] min-h-screen">
      <Header />
      <Hero />
      <Stats />
      <Campaigns />
      <AboutUs />
      <Team />
      <Testimonial />
      <CTA />
      <Footer />
    </div>
  );
}

export default App;

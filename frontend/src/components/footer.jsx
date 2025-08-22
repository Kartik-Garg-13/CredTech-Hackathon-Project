const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white pt-16 pb-8">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-80 mb-12">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <span className="font-bold text-2xl">CredTech</span>
            </div>
            <p className="text-gray-400 w-[20vw] text-sm">
              India's pioneer in blockchain-based event ticketing.
              Secure, verifiable, and collectible tickets for unforgettable experiences across the nation.
            </p>
          </div>
          
          <div>
            <h3 className="font-medium text-lg mb-4">Quick Links</h3>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-purple hover:text-white/80 transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-purple hover:text-white/80 transition-colors">How It Works</a></li>
              <li><a href="#" className="hover:text-purple hover:text-white/80 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-purple hover:text-white/80 transition-colors">Terms of Service</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-lg mb-4">Connect With Us</h3>
            <div className="flex space-x-4 mb-6">
              <a href="#" className="bg-white hover:bg-white/80 p-2 rounded-full hover:bg-purple transition-colors">
                <img src="../../socials/instagram.svg" alt="instgaram"/>
              </a>
              <a href="#" className="bg-white hover:bg-white/80 p-2 rounded-full hover:bg-purple transition-colors">
                <img src="../../socials/facebook.svg" alt="facebook"/>
              </a>
              <a href="#" className="bg-white hover:bg-white/80 p-2 rounded-full hover:bg-purple transition-colors">
                <img src="../../socials/twitter-x.svg" alt="twitter-x"/>
              </a>
              <a href="#" className="bg-white hover:bg-white/80 p-2 rounded-full hover:bg-purple transition-colors">
                <img src="../../socials/envelope.svg" alt="mail"/>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
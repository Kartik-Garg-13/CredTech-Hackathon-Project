import HomePage from './home/page';
import DashboardPage from './dashboard/page';
import Navbar from '../components/navbar';
import Footer from '../components/footer';
import { Routes, Route } from 'react-router-dom';
function App() {
  return (
    <>
              <div className="flex flex-col min-h-[100rem] bg-">
                <Navbar />
                <main className="flex-grow">
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                  </Routes>
                </main>
                <Footer/>
              </div>
    </>
  )
}

export default App

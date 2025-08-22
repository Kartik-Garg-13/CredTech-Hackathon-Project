import Intro from "../../components/intro.jsx";
import About from "../../components/about.jsx";
import FAQ from "../../components/FAQ.jsx";
function HomePage(){
    return(
        <>
        <div className="min-h-[70vh] flex flex-col items-center">
            <img src="../../../assets/bg.jpg" alt="background" className="absolute -z-10 top-0"/>
            <Intro/>
            <About/>
            <FAQ/>
        </div>
        </>
    )
}
export default HomePage;
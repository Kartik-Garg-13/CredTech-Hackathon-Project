import { useNavigate } from "react-router-dom";
function Intro() {
    const navigate = useNavigate();
    return (
        <div className="flex flex-col item-center mt-30">
            <h1 className="text-5xl md:text-7xl font-bold text-white text-center">CredTech<br />Project</h1>
            <p className="text-center text-xl md:text-2xl text-white py-5">
                Experience the future of live events with blockchain-verified<br />tickets and exclusive digital collectibles.
            </p>
            <div className="flex gap-5 justify-center">
                <button onClick={()=>navigate("/dashboard")}
                className="bg-amber-300 hover:bg-amber-300/80 text-white p-[0.7rem] px-[1rem] rounded-md cursor-pointer">
                    Go To Dashboard</button>
                <button className="bg-white border border-white hover:bg-white/20 p-[0.7rem] px-[1.5rem] rounded-md cursor-pointer">
                    Learn More</button>
            </div>
        </div>
    )
}
export default Intro;
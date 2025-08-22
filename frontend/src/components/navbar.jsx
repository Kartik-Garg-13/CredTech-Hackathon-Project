import { Link, useMatch, useResolvedPath} from "react-router-dom";
import { useState, useEffect } from "react";
function Navbar(){
    const [isScrolled, setIsScrolled] = useState(false);

    // navbar color change : 
    useEffect(() => {
        const handleScroll = () => {
            if (window.scrollY > 30) {
                setIsScrolled(true);
            } else {
                setIsScrolled(false);
            }
        };
        window.addEventListener('scroll', handleScroll);
        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);


    return(
        <>
        {/* navbar */}
        <nav className={`flex z-20 sticky text-white top-0 w-[100%] justify-between ${isScrolled ? 'bg-gray-800 py-[1.4rem]' : 'bg-transparent py-[2rem]'} text-md px-[1.4rem] transition-all duration-300`}>
            {/* logo */}
            <Link to="/" className="text-white font-bold text-[clamp(1rem,1.6vw,1.6rem)]">CredTech Project</Link>
            {/* navbar links */}
            <ul className="flex ml-[0rem] gap-[clamp(1.5rem,4vw,4rem)]">
                <CustomLink to="/dashboard">Dashboard</CustomLink>
            </ul>
        </nav>
        </>
    )
}
function CustomLink({to, children, ...props}){
    const resolvedPath = useResolvedPath(to);
    const isActive = useMatch({ path: resolvedPath.pathname, end:true })
    return(
        <>
        {/* navbar link component */}
        {/* if active ? css1 : css2 (for every other link) */}
        <li className={isActive ? "text-white font-bold duration-50 text-lg w-[clamp(3rem,10vw,10rem)] justify-center pt-1 flex" : "text-white hover:font-bold pt-1 duration-50 w-[clamp(3rem,10vw,10rem)]  text-lg justify-center flex"}>
            <Link to={to} {...props}>{children}</Link>
        </li>
        </>
    )
}
export default Navbar;
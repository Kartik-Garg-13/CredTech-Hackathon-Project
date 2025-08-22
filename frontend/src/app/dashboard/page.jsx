import FinancialDashboard from "../../components/financeDash";
function DashboardPage(){
    return(
        <>
            <div className="min-h-[100vh] flex-col flex items-center">
                <img src="../../../assets/bg1.jpg" alt="background" className="absolute -z-10 min-h-[100rem] top-0"/>
                <FinancialDashboard/>
            </div>
            
        </>
    )
}
export default DashboardPage;
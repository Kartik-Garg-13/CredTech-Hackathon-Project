import React, { useState } from 'react';

// --- Helper function to determine the color based on rating ---
const getRatingColor = (rating) => {
    switch (rating) {
        case 'AAA':
        case 'AA':
            return 'bg-green-500 text-white';
        case 'A':
        case 'BBB':
            return 'bg-yellow-500 text-white';
        case 'BB':
        case 'B':
            return 'bg-orange-500 text-white';
        case 'C':
        case 'D':
            return 'bg-red-500 text-white';
        default:
            return 'bg-gray-400 text-white';
    }
};

// --- Sub-component for a single metric ---
const Metric = ({ label, value, bucket }) => (
    <div className="p-2 bg-gray-50 rounded-md text-center">
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-lg font-semibold text-gray-800">{value ?? 'N/A'}</p>
        <p className="text-xs text-gray-400">{bucket}</p>
    </div>
);

// --- Sub-component for a single stock's card ---
const ScoreCard = ({ data }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="bg-white rounded-lg shadow-lg overflow-hidden transition-all duration-300">
            {/* --- Main Card Header --- */}
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">{data.Symbol}</h2>
                    <p className="text-sm text-gray-500">{data.Yahoo_Ticker} - {data.Tier} Cap</p>
                </div>
                <div className={`px-4 py-2 rounded-full text-lg font-bold ${getRatingColor(data.Rating)}`}>
                    {data.Rating}
                </div>
            </div>

            {/* --- Key Metrics --- */}
            <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 bg-indigo-50 rounded-lg text-center">
                    <p className="text-sm text-indigo-700">Total Score</p>
                    <p className="text-3xl font-bold text-indigo-900">{data.Total_Score}</p>
                </div>
                 <Metric label="YoY Growth" value={`${data.YoY_Growth}%`} bucket={data.YoY_Bucket} />
                 <Metric label="PAT Margin" value={`${data.PAT_Margin}%`} bucket={data.PAT_Bucket} />
                 <Metric label="30D Return" value={`${data.Stock_Return_30D}%`} bucket={data.Stock_Bucket} />
            </div>

            {/* --- Collapsible Details --- */}
            <div className="px-4 pb-4">
                <button 
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="text-sm text-indigo-600 hover:underline w-full text-left"
                >
                    {isExpanded ? 'Hide Details' : 'Show More Details'}
                </button>
                {isExpanded && (
                    <div className="mt-4 border-t pt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
                        <Metric label="Market Cap (Cr)" value={data.MarketCap_Crore} bucket={data.Tier} />
                        <Metric label="CFO/PAT Ratio" value={data.CFO_PAT_Ratio} bucket={data.CFO_PAT_Bucket} />
                        <Metric label="CFI/Revenue" value={data.CFI_Revenue} bucket={data.CFI_Bucket} />
                        <Metric label="Borrowing Growth" value={`${data.Borrowing_Growth_}%`} bucket={data.Borrowing_Bucket} />
                        <Metric label="Event Score" value={data.Event_Score} bucket="" />
                    </div>
                )}
            </div>
        </div>
    );
};


// --- Main Dashboard Component ---
function FinancialDashboard() {
    const [tickerInput, setTickerInput] = useState("RELIANCE, TCS, TATAMOTORS");
    const [scores, setScores] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchScores = async () => {
        setIsLoading(true);
        setError(null);
        setScores([]);

        // --- FIX IS HERE ---
        // 1. Split the input string into individual tickers.
        // 2. For each ticker, trim whitespace and convert to uppercase.
        // 3. Check if it already ends with '.NS'. If not, append it.
        // 4. Filter out any empty strings that might result from extra commas.
        const symbols = tickerInput
            .split(',')
            .map(s => {
                const trimmed = s.trim().toUpperCase();
                if (trimmed && !trimmed.endsWith('.NS')) {
                    return `${trimmed}.NS`;
                }
                return trimmed;
            })
            .filter(s => s); // Filter out empty strings

        if (symbols.length === 0) {
            setError("Please enter at least one valid stock ticker.");
            setIsLoading(false);
            return;
        }

        try {
            // Replace with your actual backend URL
            const response = await fetch('http://127.0.0.1:8000/api/get-scores', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbols }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            setScores(data.scores);

        } catch (e) {
            setError("Failed to fetch scores. Please ensure the backend server is running and the tickers are valid.");
            console.error("Fetch error:", e);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-gray-100 min-h-screen p-4 sm:p-6 md:p-8">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">Credit Score Dashboard</h1>
                <p className="text-gray-600 mb-6">Enter Indian stock tickers (e.g., RELIANCE, TCS) to get their financial health rating.</p>

                {/* --- Input Section --- */}
                <div className="bg-white p-4 rounded-lg shadow-md mb-8">
                    <textarea
                        value={tickerInput}
                        onChange={(e) => setTickerInput(e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        placeholder="Enter stock tickers, separated by commas (e.g., RELIANCE, TCS)"
                        rows="3"
                    />
                    <button 
                        onClick={fetchScores} 
                        disabled={isLoading} 
                        className="mt-3 w-full bg-indigo-600 text-white font-bold py-3 px-4 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300 transition-colors duration-300"
                    >
                        {isLoading ? 'Analyzing...' : 'Get Credit Scores'}
                    </button>
                </div>

                {/* --- Results Section --- */}
                {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md" role="alert">{error}</div>}
                
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
                    {scores.map((scoreData, index) => (
                        <ScoreCard key={scoreData.Yahoo_Ticker || index} data={scoreData} />
                    ))}
                </div>
            </div>
        </div>
    );
}

export default FinancialDashboard;

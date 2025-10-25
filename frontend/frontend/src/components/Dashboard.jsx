import { useEffect, useState } from "react";
import api from "../api";

export default function Dashboard({ onLogout }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/dashboard/summary")
      .then(res => setData(res.data))
      .catch(() => setData({ error: "Failed to load" }));
  }, []);

  if (!data) return <div className="p-10">Loading dashboard...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">🏦 Banking Dashboard</h1>
        <button
          onClick={() => {
            localStorage.removeItem("token");
            onLogout();
          }}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Account Summary</h2>
          <pre className="text-sm">{JSON.stringify(data.account_summary, null, 2)}</pre>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Transactions (7 days)</h2>
          <pre className="text-sm">{JSON.stringify(data.transaction_trends, null, 2)}</pre>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Loan Status</h2>
          <pre className="text-sm">{JSON.stringify(data.loan_repayment_status, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
}

import React from "react";

const GenerateReportButton = () => {
  const handleGenerateReport = async () => {
    try {
      const res = await fetch("http://localhost:5002/api/generate-report", {
        method: "POST",
      });

      const data = await res.json();

      if (data.status === "success") {
        alert("Report generated successfully!");
      } else {
        alert(`Report failed: ${data.message}`);
      }
    } catch (err) {
      console.error("Error generating report:", err);
      alert("Failed to connect to the backend.");
    }
  };

  return (
    <button
      onClick={handleGenerateReport}
      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded mt-4 transition"
    >
      📦 Generate Report
    </button>
  );
};

export default GenerateReportButton;
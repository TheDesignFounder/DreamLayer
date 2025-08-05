import { useEffect, useState } from "react";

const InferenceBadge = () => {
  const [badge, setBadge] = useState("⏱ Loading...");

  useEffect(() => {
    fetch("/internal/inference/badge")
      .then((res) => res.json())
      .then((data) => setBadge(data.badge || "N/A"))
      .catch((err) => {
        console.error("Badge fetch failed", err);
        setBadge("⚠️ Error");
      });
  }, []);

  return (
    <div className="rounded bg-gray-100 px-3 py-1 text-sm text-gray-600 shadow-sm ml-4">
      {badge}
    </div>
  );
};

export default InferenceBadge;

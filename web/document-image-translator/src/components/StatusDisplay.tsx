import React from "react";
import type { StatusDisplayProps } from "@/types";

const StatusDisplay: React.FC<StatusDisplayProps> = ({ status }) => {
  if (!status) return null;
  return (
    <div className="mt-4 p-4 border rounded bg-gray-100 w-full max-w-md">
      <div>Status: <b>{status.status}</b></div>
      {status.updated_at && <div>Last updated: {status.updated_at}</div>}
      {status.error && <div className="text-red-600">Error: {status.error}</div>}
    </div>
  );
};

export default StatusDisplay;

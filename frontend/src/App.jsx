import React from "react";
import { generationLimits } from "@weekly-status/contracts";

export default function App() {
  return (
    <main>
      <h1>Jira Weekly Status Reports</h1>
      <p>The report workspace is ready for feature implementation.</p>
      <p>
        Shared API contract loaded (up to {generationLimits.riskItems.maxItems}{" "}
        risk entries).
      </p>
    </main>
  );
}

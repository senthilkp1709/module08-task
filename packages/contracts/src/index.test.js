import assert from "node:assert/strict";
import { test } from "node:test";
import { generationLimits, reportApiSchema } from "./index.js";

test("shared report API contract exposes the specified request limits", () => {
  assert.equal(reportApiSchema.$defs.generateReportRequest.additionalProperties, false);
  assert.equal(generationLimits.preparedBy.maxLength, 120);
  assert.equal(generationLimits.executiveSummary.maxLength, 2000);
  assert.equal(generationLimits.riskItems.maxItems, 20);
  assert.equal(generationLimits.riskItems.items.maxLength, 2000);
});

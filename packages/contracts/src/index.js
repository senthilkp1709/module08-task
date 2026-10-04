import reportApiSchema from "./report-api.schema.json" with { type: "json" };

export const generationLimits = Object.freeze({
  preparedBy: reportApiSchema.$defs.generateReportRequest.properties.preparedBy,
  executiveSummary:
    reportApiSchema.$defs.generateReportRequest.properties.executiveSummary,
  riskItems: reportApiSchema.$defs.generateReportRequest.properties.riskItems
});

export { reportApiSchema };

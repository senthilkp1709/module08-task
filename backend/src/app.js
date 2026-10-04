import express from "express";
import { reportApiSchema } from "@weekly-status/contracts";

export function createApp() {
  const app = express();
  app.disable("x-powered-by");
  app.use(express.json());
  app.locals.reportApiSchema = reportApiSchema;

  app.get("/", (_request, response) => {
    response.json({ service: "jira-weekly-status-report-api" });
  });

  return app;
}
import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { createApp } from "./app.js";

let server;
let baseUrl;

before(async () => {
  server = createApp().listen(0, "127.0.0.1");
  await new Promise((resolve, reject) => {
    server.once("listening", resolve);
    server.once("error", reject);
  });
  const { port } = server.address();
  baseUrl = `http://127.0.0.1:${port}`;
});

after(async () => {
  if (server) {
    await new Promise((resolve, reject) => {
      server.close((error) => (error ? reject(error) : resolve()));
    });
  }
});

test("API scaffold responds without exposing configuration", async () => {
  const response = await fetch(baseUrl);

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    service: "jira-weekly-status-report-api"
  });
  assert.equal(response.headers.get("x-powered-by"), null);
});

test("backend consumes the shared API contract", () => {
  assert.equal(
    createApp().locals.reportApiSchema.$defs.generateReportRequest.additionalProperties,
    false
  );
});

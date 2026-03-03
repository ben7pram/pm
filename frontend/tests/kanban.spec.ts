import { expect, test } from "@playwright/test";

// helper to perform login if needed
async function ensureLoggedIn(page: any) {
  await page.goto("/");
  // sanity-check that /api/hello proxies to backend correctly
  const hello = await page.evaluate(() =>
    fetch("/api/hello").then((r) => r.json()).catch((e) => ({ error: e.toString() }))
  );
  console.log("api/hello returned", hello);

  // rather than wait for a specific request, just wait for either the login
  // form or the Kanban heading to appear so we know the initial loading is
  // done
  await Promise.race([
    page.getByRole("heading", { name: /sign in/i }).waitFor(),
    page.getByRole("heading", { name: "Kanban Studio" }).waitFor(),
  ]);

  const loginCount = await page.getByRole("heading", { name: /sign in/i }).count();
  if (loginCount > 0) {
    await page.getByLabel("Username").fill("user");
    await page.getByLabel("Password").fill("password");

    // log login request/response for debugging
    page.on("request", (req) => {
      if (req.url().endsWith("/api/login")) {
        console.log("login request url", req.url(), "method", req.method(), "body", req.postData());
      }
    });
    page.on("response", async (resp) => {
      if (resp.url().endsWith("/api/login")) {
        console.log("login response status", resp.status());
        try {
          console.log("login response body", await resp.text());
        } catch {}
      }
    });

    await page.getByRole("button", { name: /sign in/i }).click();
    try {
      await page.getByRole("heading", { name: "Kanban Studio" }).waitFor({ timeout: 10000 });
    } catch (err) {
      // output debugging information
      console.log("--- page content after login attempt ---");
      console.log(await page.content());
      console.log("--- cookies ---");
      console.log(await page.context().cookies());
      throw err;
    }
  }
}

test("loads the kanban board", async ({ page }) => {
  await ensureLoggedIn(page);
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await ensureLoggedIn(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await ensureLoggedIn(page);
  const card = page.getByTestId("card-card-1");
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});

import { expect, test } from "@playwright/test";

// helper to perform a fake login by stubbing the backend API. This
// allows us to exercise the real UI (clicking the form) while avoiding any
// problems with the dev-server proxy or cookies. It also keeps the board
// interactions network‑free since the data is static.
async function ensureLoggedIn(page: any) {
  // show browser console messages so debugging is easier.
  page.on("console", (msg) => {
    console.log("PAGE CONSOLE:", msg.text());
  });

  // stub login and me endpoints to return successful responses
  await page.route("**/api/login", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ authenticated: true }),
    });
  });
  await page.route("**/api/me", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ authenticated: true }),
    });
  });

  // stub board endpoint with initial data
  const initialBoardData = {
    columns: [
      { id: "col-todo", title: "To Do", cardIds: ["card-1", "card-2"] },
      { id: "col-progress", title: "In Progress", cardIds: ["card-3"] },
      { id: "col-review", title: "Review", cardIds: [] },
      { id: "col-done", title: "Done", cardIds: ["card-4"] },
      { id: "col-ideas", title: "Ideas", cardIds: [] },
    ],
    cards: {
      "card-1": { id: "card-1", title: "Design system", details: "Create a reusable design system" },
      "card-2": { id: "card-2", title: "Prototypes", details: "Build interactive prototypes" },
      "card-3": { id: "card-3", title: "Code review", details: "Review pull requests" },
      "card-4": { id: "card-4", title: "Deployment", details: "Deploy to production" },
    },
  };
  
  await page.route("**/api/board", (route) => {
    if (route.request().method() === "GET") {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ board: { data: initialBoardData } }),
      });
    } else if (route.request().method() === "POST") {
      // accept POST and just return ok, don't update anything
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true }),
      });
    }
  });

  await page.goto("/");
  // if login form is visible, drive it
  const loginCount = await page.getByRole("heading", { name: /sign in/i }).count();
  if (loginCount > 0) {
    await page.getByLabel("Username").fill("user");
    await page.getByLabel("Password").fill("password");
    await page.getByRole("button", { name: /sign in/i }).click();
  }

  // by now the board should be visible
  await page.getByRole("heading", { name: "Kanban Studio" }).waitFor();
}

test("shows login form when unauthenticated", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
});

test("login form shows error on bad credentials", async ({ page }) => {
  await page.goto("/");
  // stub the backend response to simulate a 401 without hitting real server
  await page.route("**/api/login", (route) => {
    route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ authenticated: false }) });
  });

  await page.getByLabel("Username").fill("wrong");
  await page.getByLabel("Password").fill("wrong");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByText("Invalid credentials")).toBeVisible();
});

// exercise logout using a stubbed /api/logout so the UI goes back to login.
// login itself is handled by cookie injection.
// Remaining tests use the helper that stubs authentication.

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

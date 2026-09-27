const { chromium } = require("playwright");

const SCHOOL_URL =
  "https://selectschool.sparx-learning.com/?app=sparx_maths&forget=1";

function send(data) {
  process.stdout.write(JSON.stringify(data));
}

async function findSchoolInput(page) {
  const selectors = [
    'input[placeholder="Start typing your school\'s name..."]',
    'input[placeholder*="Start typing your school"]',
    'input[type="search"]',
    'input[type="text"]',
    '[role="textbox"]'
  ];

  for (const frame of page.frames()) {
    for (const selector of selectors) {
      try {
        const input = frame.locator(selector).first;

        if (await input.count() > 0) {
          await input.waitFor({
            state: "visible",
            timeout: 10000
          });

          return input;
        }
      } catch {}
    }
  }

  return null;
}

async function findButton(page, name) {
  for (const frame of page.frames()) {
    try {
      const button = frame
        .getByRole("button", {
          name,
          exact: true
        })
        .first;

      if (await button.count() > 0) {
        await button.waitFor({
          state: "visible",
          timeout: 10000
        });

        return button;
      }
    } catch {}
  }

  return null;
}

async function login(username, password, school) {
  const browser = await chromium.launch({
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage"
    ]
  });

  try {
    const context = await browser.newContext({
      viewport: {
        width: 1280,
        height: 900
      }
    });

    const page = await context.newPage();

    await page.goto(SCHOOL_URL, {
      waitUntil: "domcontentloaded",
      timeout: 60000
    });

    await page.waitForTimeout(3000);

    const schoolInput = await findSchoolInput(page);

    if (!schoolInput) {
      throw new Error(
        "Could not find the Sparx school search box."
      );
    }

    await schoolInput.fill(school);

    await page.waitForTimeout(2000);

    let schoolResult = null;

    for (const frame of page.frames()) {
      const elements = frame.locator(
        '[role="option"], li, button'
      );

      const count = Math.min(
        await elements.count(),
        50
      );

      for (let i = 0; i < count; i++) {
        try {
          const element = elements.nth(i);

          if (!await element.isVisible()) {
            continue;
          }

          const text = (
            await element.innerText()
          ).trim();

          if (
            text.toLowerCase().includes(
              school.toLowerCase()
            )
          ) {
            schoolResult = element;
            break;
          }
        } catch {}
      }

      if (schoolResult) break;
    }

    if (schoolResult) {
      await schoolResult.click();
      await page.waitForTimeout(500);
    }

    const continueButton =
      await findButton(page, "Continue");

    if (!continueButton) {
      throw new Error(
        "Could not find the Sparx Continue button."
      );
    }

    await continueButton.click();

    await page.waitForTimeout(3000);

    let usernameInput = null;
    let passwordInput = null;

    for (const frame of page.frames()) {
      try {
        const inputs = frame.locator("input");
        const count = await inputs.count();

        for (let i = 0; i < count; i++) {
          const input = inputs.nth(i);

          if (!await input.isVisible()) {
            continue;
          }

          const type = (
            await input.getAttribute("type") || ""
          ).toLowerCase();

          if (type === "password") {
            passwordInput = input;
          } else if (
            !usernameInput &&
            (type === "" || type === "text")
          ) {
            usernameInput = input;
          }
        }
      } catch {}
    }

    if (!usernameInput) {
      throw new Error(
        "Could not find the Sparx username field."
      );
    }

    if (!passwordInput) {
      throw new Error(
        "Could not find the Sparx password field."
      );
    }

    await usernameInput.fill(username);
    await passwordInput.fill(password);

    let loginButton =
      await findButton(page, "Log in");

    if (!loginButton) {
      loginButton =
        await findButton(page, "Login");
    }

    if (!loginButton) {
      throw new Error(
        "Could not find the Sparx login button."
      );
    }

    await loginButton.click();

    await page.waitForTimeout(4000);

    return {
      success: true,
      storage_state:
        await context.storageState()
    };
  } finally {
    await browser.close();
  }
}

async function main() {
  let input = "";

  process.stdin.setEncoding("utf8");

  for await (const chunk of process.stdin) {
    input += chunk;
  }

  try {
    const request = JSON.parse(input);

    if (
      !request.username ||
      !request.password ||
      !request.school
    ) {
      throw new Error(
        "Missing Sparx login information."
      );
    }

    const result = await login(
      request.username,
      request.password,
      request.school
    );

    send(result);
  } catch (error) {
    send({
      success: false,
      error: error.message
    });

    process.exitCode = 1;
  }
}

main();

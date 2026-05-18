import { spawn } from "node:child_process";

const pythonPort = process.env.PYTHON_API_PORT ?? "8000";
const pythonApiUrl =
  process.env.PYTHON_API_URL ?? `http://127.0.0.1:${pythonPort}`;

const children = [
  spawn(
    "python3",
    ["-m", "startup_search.server"],
    {
      env: {
        ...process.env,
        PYTHONPATH: "python",
        PYTHON_API_PORT: pythonPort,
        PYTHON_API_URL: pythonApiUrl,
      },
      stdio: "inherit",
    },
  ),
  spawn(
    process.platform === "win32" ? "next.cmd" : "next",
    ["dev"],
    {
      env: {
        ...process.env,
        PYTHON_API_URL: pythonApiUrl,
        NEXT_PUBLIC_PYTHON_API_URL: pythonApiUrl,
      },
      stdio: "inherit",
    },
  ),
];

let shuttingDown = false;

function shutdown(signal) {
  if (shuttingDown) {
    return;
  }
  shuttingDown = true;
  for (const child of children) {
    if (!child.killed) {
      child.kill(signal);
    }
  }
}

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => shutdown(signal));
}

for (const child of children) {
  child.on("exit", (code) => {
    if (!shuttingDown && code && code !== 0) {
      shutdown("SIGTERM");
      process.exitCode = code;
    }
  });
}

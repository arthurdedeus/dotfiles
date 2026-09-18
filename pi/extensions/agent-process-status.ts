import { execFile } from "node:child_process";
import { readdir, readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { sep } from "node:path";
import { promisify } from "node:util";

import type { AssistantMessage } from "@earendil-works/pi-ai";
import type {
  ExtensionAPI,
  ExtensionContext,
  ReadonlyFooterDataProvider,
} from "@earendil-works/pi-coding-agent";
import { truncateToWidth, visibleWidth } from "@earendil-works/pi-tui";

const execFileAsync = promisify(execFile);
const REFRESH_INTERVAL_MS = 5000;
const STATUS_DIRECTORY = "/tmp/pi-subagents";
const STATUS_KEY = "agent-process-status";
const ACTIVE_AGENT_STATES = new Set([
  "starting",
  "prompted",
  "running",
  "settled",
  "stopping",
  "reader_failed",
]);

interface ProcessRecord {
  pid: number;
  ppid: number;
  command: string;
}

interface ProcessCounts {
  agents: number;
  background: number;
  otherPiSessions: number;
}

function isActiveAgentStatus(value: unknown): boolean {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return false;
  }
  const state = (value as Record<string, unknown>).state;
  return typeof state === "string" && ACTIVE_AGENT_STATES.has(state);
}

async function getActiveAgentCount(): Promise<number> {
  try {
    const entries = await readdir(STATUS_DIRECTORY, { withFileTypes: true });
    const statuses = await Promise.all(
      entries
        .filter((entry) => entry.isFile() && entry.name.endsWith(".status.json"))
        .map(async (entry) => {
          try {
            return JSON.parse(
              await readFile(`${STATUS_DIRECTORY}/${entry.name}`, "utf8"),
            ) as unknown;
          } catch {
            return null;
          }
        }),
    );
    return statuses.filter(isActiveAgentStatus).length;
  } catch {
    return 0;
  }
}

function parseProcesses(stdout: string): ProcessRecord[] {
  return stdout
    .split("\n")
    .map((line) => {
      const parts = line.trim().split(/\s+/);
      if (parts.length < 3) return null;
      const pid = Number(parts[0]);
      const ppid = Number(parts[1]);
      if (!Number.isInteger(pid) || !Number.isInteger(ppid)) return null;
      return { pid, ppid, command: parts.slice(2).join(" ") };
    })
    .filter((process): process is ProcessRecord => process !== null);
}

function isPiProcess(process: ProcessRecord): boolean {
  return (
    /(?:^|\/)pi(?:\s|$)/.test(process.command) &&
    process.pid !== globalThis.process.pid
  );
}

function isHeadlessAgentProcess(process: ProcessRecord): boolean {
  if (/\b(?:codex|claude)\b/.test(process.command)) {
    return /\bexec\b|--bg|--background|\bbabysit\b|\bsubagent\b/.test(
      process.command,
    );
  }
  return (
    isPiProcess(process) &&
    /--mode\s+(?:json|rpc)|--no-session/.test(process.command)
  );
}

function countProcesses(
  processes: ProcessRecord[],
  activeAgentCount: number,
): ProcessCounts {
  const piProcesses = processes.filter(isPiProcess);
  const agentProcesses = processes.filter(isHeadlessAgentProcess);
  const agentPids = new Set(agentProcesses.map((process) => process.pid));
  const roots = agentProcesses.filter(
    (process) => !agentPids.has(process.ppid),
  );
  return {
    agents: activeAgentCount,
    background: roots.filter((process) => process.ppid === 1).length,
    otherPiSessions:
      piProcesses.length - agentProcesses.filter(isPiProcess).length,
  };
}

async function getProcessCounts(): Promise<ProcessCounts> {
  const activeAgentCount = await getActiveAgentCount();
  try {
    const { stdout } = await execFileAsync(
      "ps",
      ["-axo", "pid=,ppid=,command="],
      { encoding: "utf8" },
    );
    return countProcesses(parseProcesses(String(stdout)), activeAgentCount);
  } catch {
    return { agents: activeAgentCount, background: 0, otherPiSessions: 0 };
  }
}

function formatTokens(count: number): string {
  if (count < 1000) return count.toString();
  if (count < 10000) return `${(count / 1000).toFixed(1)}k`;
  if (count < 1000000) return `${Math.round(count / 1000)}k`;
  return `${(count / 1000000).toFixed(1)}M`;
}

function formatCwd(cwd: string): string {
  const home = homedir();
  if (cwd === home) return "~";
  return cwd.startsWith(`${home}${sep}`) ? `~${cwd.slice(home.length)}` : cwd;
}

function sanitizeStatusText(text: string): string {
  return text
    .replace(/[\r\n\t]/g, " ")
    .replace(/ +/g, " ")
    .trim();
}

function getUsage(ctx: ExtensionContext): {
  input: number;
  output: number;
  cost: number;
} {
  let input = 0;
  let output = 0;
  let cost = 0;
  for (const entry of ctx.sessionManager.getEntries()) {
    if (entry.type !== "message") continue;
    if (entry.message.role !== "assistant") continue;
    const message = entry.message as AssistantMessage;
    input += message.usage.input;
    output += message.usage.output;
    cost += message.usage.cost.total;
  }
  return { input, output, cost };
}

function renderFooter(
  width: number,
  ctx: ExtensionContext,
  counts: ProcessCounts | null,
  theme: ExtensionContext["ui"]["theme"],
  footerData: ReadonlyFooterDataProvider,
): string[] {
  const branch = footerData.getGitBranch();
  const branchSuffix = branch ? ` (${branch})` : "";
  const location = truncateToWidth(
    `${formatCwd(ctx.cwd)}${branchSuffix}`,
    width,
    "...",
  );
  const usage = getUsage(ctx);
  const stats = [
    `↑${formatTokens(usage.input)}`,
    `↓${formatTokens(usage.output)}`,
    `$${usage.cost.toFixed(3)}`,
  ];
  const contextUsage = ctx.getContextUsage();
  const contextWindow =
    contextUsage?.contextWindow ?? ctx.model?.contextWindow ?? 0;
  const contextPercent = contextUsage?.percent;
  const contextText =
    contextPercent === null || contextPercent === undefined
      ? `?/${formatTokens(contextWindow)}`
      : `${contextPercent.toFixed(1)}%/${formatTokens(contextWindow)}`;
  const contextDisplay =
    contextPercent !== null &&
    contextPercent !== undefined &&
    contextPercent > 90
      ? theme.fg("error", contextText)
      : contextPercent !== null &&
          contextPercent !== undefined &&
          contextPercent > 70
        ? theme.fg("warning", contextText)
        : contextText;
  stats.push(contextDisplay);

  const model = ctx.model?.id ?? "no-model";
  const agentStatus = counts
    ? `Pi sessions ${counts.otherPiSessions} · subagents ${counts.agents} · background ${counts.background}`
    : "Pi sessions ? · subagents ? · background ?";
  const left = theme.fg("dim", stats.join(" "));
  const right = theme.fg("dim", model);
  const available = width - visibleWidth(left) - visibleWidth(right);
  const secondLine =
    available >= 1
      ? `${left}${" ".repeat(available)}${right}`
      : truncateToWidth(`${left} ${right}`, width, "");
  const agentStatusDisplay = theme.fg("dim", agentStatus);
  const extensionStatuses = Array.from(
    footerData.getExtensionStatuses().entries(),
  )
    .filter(([key]) => key !== STATUS_KEY)
    .map(([, status]) => sanitizeStatusText(status))
    .filter(Boolean);
  const extensionStatusDisplay =
    extensionStatuses.length > 0 ? extensionStatuses.join(" ") : "";
  const extensionStatusWidth = visibleWidth(extensionStatusDisplay);
  const agentStatusWidth = visibleWidth(agentStatusDisplay);
  const statusLine =
    extensionStatusWidth + agentStatusWidth + 1 <= width
      ? `${extensionStatusDisplay}${" ".repeat(width - extensionStatusWidth - agentStatusWidth)}${agentStatusDisplay}`
      : `${truncateToWidth(extensionStatusDisplay, Math.max(0, width - agentStatusWidth - 1), "")}${" ".repeat(
          Math.max(
            1,
            width -
              Math.min(extensionStatusWidth, width - agentStatusWidth - 1) -
              agentStatusWidth,
          ),
        )}${agentStatusDisplay}`;
  return [location, secondLine, truncateToWidth(statusLine, width, "")];
}

export default function (pi: ExtensionAPI): void {
  let timer: ReturnType<typeof setInterval> | undefined;
  let refreshInFlight = false;
  let counts: ProcessCounts | null = null;
  let requestRender: (() => void) | undefined;

  const refresh = async (): Promise<void> => {
    if (refreshInFlight) return;
    refreshInFlight = true;
    try {
      counts = await getProcessCounts();
      requestRender?.();
    } finally {
      refreshInFlight = false;
    }
  };

  const stop = (ctx: ExtensionContext): void => {
    if (timer) {
      clearInterval(timer);
      timer = undefined;
    }
    requestRender = undefined;
    counts = null;
    ctx.ui.setFooter(undefined);
  };

  pi.on("session_start", async (_event, ctx) => {
    stop(ctx);
    ctx.ui.setFooter((tui, theme, footerData) => {
      requestRender = () => tui.requestRender();
      const unsubscribe = footerData.onBranchChange(() => tui.requestRender());
      return {
        dispose: () => {
          unsubscribe();
          requestRender = undefined;
        },
        invalidate() {},
        render: (width: number): string[] =>
          renderFooter(width, ctx, counts, theme, footerData),
      };
    });
    void refresh();
    timer = setInterval(() => void refresh(), REFRESH_INTERVAL_MS);
  });

  pi.on("session_shutdown", async (_event, ctx) => {
    stop(ctx);
  });
}

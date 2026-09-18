import type { Dirent } from "node:fs";
import { readdir, readFile } from "node:fs/promises";

import type {
  ExtensionAPI,
  ExtensionContext,
} from "@earendil-works/pi-coding-agent";
import { Key, matchesKey, truncateToWidth } from "@earendil-works/pi-tui";

const STATUS_DIRECTORY = "/tmp/pi-subagents";
const REFRESH_INTERVAL_MS = 1000;
const ACTIVE_STATES = new Set([
  "starting",
  "prompted",
  "running",
  "settled",
  "stopping",
  "reader_failed",
]);

interface AgentStatus {
  name: string;
  runId: string;
  parentSessionId: string | null;
  taskSummary: string;
  state: string;
  model: string;
  toolCalls: number;
  currentTool: string | null;
  tokens: Record<string, unknown> | null;
  startedAt: number;
  stalled: boolean;
}

interface RenderTui {
  requestRender(): void;
}

function getString(value: Record<string, unknown>, key: string): string | null {
  const candidate = value[key];
  return typeof candidate === "string" && candidate.trim() ? candidate : null;
}

function getNumber(value: Record<string, unknown>, key: string): number {
  const candidate = value[key];
  return typeof candidate === "number" && Number.isFinite(candidate)
    ? candidate
    : 0;
}

function getTokens(
  value: Record<string, unknown>,
): Record<string, unknown> | null {
  const candidate = value.tokens;
  return candidate && typeof candidate === "object" && !Array.isArray(candidate)
    ? (candidate as Record<string, unknown>)
    : null;
}

function parseStatus(value: unknown): AgentStatus | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }

  const status = value as Record<string, unknown>;
  const name = getString(status, "name");
  const state = getString(status, "state");
  if (!name || !state) {
    return null;
  }

  return {
    name,
    runId: getString(status, "runId") ?? "legacy",
    parentSessionId: getString(status, "parentSessionId"),
    taskSummary: getString(status, "taskSummary") ?? name,
    state,
    model: getString(status, "model") ?? "unknown model",
    toolCalls: getNumber(status, "toolCalls"),
    currentTool: getString(status, "currentTool"),
    tokens: getTokens(status),
    startedAt: getNumber(status, "startedAt"),
    stalled: status.stalled === true,
  };
}

async function listActiveAgents(): Promise<AgentStatus[]> {
  let entries: Dirent[];
  try {
    entries = await readdir(STATUS_DIRECTORY, { withFileTypes: true });
  } catch {
    return [];
  }

  const statuses = await Promise.all(
    entries
      .filter((entry) => entry.isFile() && entry.name.endsWith(".status.json"))
      .map(async (entry): Promise<AgentStatus | null> => {
        try {
          return parseStatus(
            JSON.parse(
              await readFile(`${STATUS_DIRECTORY}/${entry.name}`, "utf8"),
            ),
          );
        } catch {
          return null;
        }
      }),
  );

  return statuses
    .filter(
      (status): status is AgentStatus =>
        status !== null && ACTIVE_STATES.has(status.state),
    )
    .sort((left, right) => left.startedAt - right.startedAt);
}

function getTokenTotal(tokens: Record<string, unknown> | null): number {
  if (!tokens) {
    return 0;
  }

  for (const key of ["totalTokens", "total"]) {
    const value = tokens[key];
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
  }

  return ["input", "output", "cacheRead", "cacheWrite"].reduce((total, key) => {
    const value = tokens[key];
    return (
      total + (typeof value === "number" && Number.isFinite(value) ? value : 0)
    );
  }, 0);
}

function formatTokens(value: number): string {
  if (value < 1000) {
    return value.toString();
  }
  if (value < 1_000_000) {
    return `${(value / 1000).toFixed(1)}k`;
  }
  return `${(value / 1_000_000).toFixed(1)}M`;
}

function formatSession(status: AgentStatus, currentSessionId: string): string {
  if (!status.parentSessionId) {
    return "session unknown";
  }
  if (status.parentSessionId === currentSessionId) {
    return "this session";
  }
  return `session ${status.parentSessionId.slice(0, 8)}`;
}

class AgentsMonitor {
  private agents: AgentStatus[] = [];
  private timer: ReturnType<typeof setInterval> | undefined;
  private loading = true;

  constructor(
    private readonly tui: RenderTui,
    private readonly theme: ExtensionContext["ui"]["theme"],
    private readonly currentSessionId: string,
    private readonly done: () => void,
  ) {}

  start(): void {
    void this.refresh();
    this.timer = setInterval(() => void this.refresh(), REFRESH_INTERVAL_MS);
  }

  stop(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
  }

  handleInput(data: string): void {
    if (
      matchesKey(data, Key.escape) ||
      data === "q" ||
      matchesKey(data, Key.enter)
    ) {
      this.stop();
      this.done();
    }
  }

  render(width: number): string[] {
    const lines = [
      this.theme.fg("accent", this.theme.bold("Active subagents")),
    ];
    if (this.loading) {
      lines.push(this.theme.fg("muted", "Loading status files..."));
    } else if (this.agents.length === 0) {
      lines.push(this.theme.fg("muted", "No active subagents."));
    } else {
      for (const [index, agent] of this.agents.entries()) {
        const state = agent.stalled
          ? "stalled"
          : agent.currentTool
            ? `using ${agent.currentTool}`
            : agent.state;
        lines.push(
          `${this.theme.fg("muted", `-> ${index + 1}: `)}${this.theme.fg("text", agent.taskSummary)}${this.theme.fg(
            "dim",
            ` - ${agent.model} - ${formatTokens(getTokenTotal(agent.tokens))} tokens - ${agent.toolCalls} tool calls - ${state}`,
          )}`,
        );
        lines.push(
          this.theme.fg(
            "dim",
            `   ${formatSession(agent, this.currentSessionId)} · ${agent.name} · ${agent.runId.slice(0, 8)}`,
          ),
        );
      }
    }
    lines.push(this.theme.fg("dim", "Enter, q, or Esc to close"));
    return lines.map((line) => truncateToWidth(line, width));
  }

  invalidate(): void {}

  private async refresh(): Promise<void> {
    this.agents = await listActiveAgents();
    this.loading = false;
    this.tui.requestRender();
  }
}

export default function (pi: ExtensionAPI): void {
  pi.registerCommand("agents", {
    description: "Monitor active Pi subagents",
    handler: async (_args, ctx) => {
      if (ctx.mode !== "tui") {
        ctx.ui.notify(
          "The agents monitor requires the interactive TUI.",
          "warning",
        );
        return;
      }

      let monitor: AgentsMonitor | undefined;
      await ctx.ui.custom<void>((tui, theme, _keybindings, done) => {
        monitor = new AgentsMonitor(
          tui,
          theme,
          ctx.sessionManager.getSessionId(),
          done,
        );
        monitor.start();
        return monitor;
      });
      monitor?.stop();
    },
  });
}

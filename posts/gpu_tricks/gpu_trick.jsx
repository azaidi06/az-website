import { useState } from "react";

const colors = {
  bg: "#0a0e17",
  surface: "#111827",
  surfaceLight: "#1a2235",
  border: "#1e2d4a",
  text: "#e2e8f0",
  textMuted: "#8b9cc0",
  accent: "#60a5fa",
  accentGlow: "rgba(96, 165, 250, 0.15)",
  green: "#34d399",
  greenGlow: "rgba(52, 211, 153, 0.15)",
  red: "#f87171",
  redGlow: "rgba(248, 113, 113, 0.12)",
  orange: "#fbbf24",
  orangeGlow: "rgba(251, 191, 36, 0.12)",
  purple: "#a78bfa",
};

const phases = [
  {
    id: 0, label: "Before", tag: "Lambda + EC2", time: "~18 min",
    color: colors.red, glow: colors.redGlow,
    title: "Two-Service Architecture",
    subtitle: "Video crosses the network 3 times through 2 services",
    wallMin: 18, fps: null, cost: 0.14, dataMB: 957, services: 2,
  },
  {
    id: 1, label: "Phase 1", tag: "NVENC", time: "~12 min",
    color: colors.orange, glow: colors.orangeGlow,
    title: "Merge Services + NVENC Transcode",
    subtitle: "NVENC hardware encode replaces 7-min Lambda CPU transcode",
    wallMin: 12, fps: 32.5, cost: 0.08, dataMB: 433, services: 1,
    decode: "cv2 CPU decode + preprocess", inference: "Eager PyTorch",
    cpuPct: 100, cudaPct: 50, nvdecIdle: true,
    labelTime: "~10 min", labelFps: "32.5 fps",
  },
  {
    id: 2, label: "Phase 2", tag: "NVDEC", time: "~9 min",
    color: colors.accent, glow: colors.accentGlow,
    title: "Hardware Decode + Threaded Overlap",
    subtitle: "NVDEC decode flips bottleneck from CPU to GPU",
    wallMin: 9, fps: 40.1, cost: 0.064, dataMB: 433, services: 1,
    decode: "NVDEC h264_cuvid + preprocess", inference: "Eager PyTorch",
    cpuPct: 36, cudaPct: 90, nvdecIdle: false,
    labelTime: "~8.1 min", labelFps: "40.1 fps",
  },
  {
    id: 3, label: "Phase 3", tag: "compile", time: "~6 min",
    color: colors.green, glow: colors.greenGlow,
    title: "torch.compile (inductor)",
    subtitle: "RTMDet 2.2x + ViTPose 1.08x → 1.77x E2E",
    wallMin: 6, fps: 57.5, cost: 0.04, dataMB: 433, services: 1,
    decode: "NVDEC h264_cuvid + preprocess", inference: "torch.compile (inductor)",
    cpuPct: 50, cudaPct: 86, nvdecIdle: false,
    labelTime: "~5.5 min", labelFps: "57.5 fps",
  },
];

/* ── Shared primitives ──────────────────────────────────────────────── */

const Arrow = ({ color = colors.textMuted }) => (
  <div style={{ display: "flex", justifyContent: "center", padding: "4px 0" }}>
    <svg width="20" height="28" viewBox="0 0 20 28">
      <line x1="10" y1="0" x2="10" y2="22" stroke={color} strokeWidth="2" strokeDasharray="4,3" />
      <polygon points="4,20 10,28 16,20" fill={color} />
    </svg>
  </div>
);

const DataBadge = ({ size, color = colors.orange }) => (
  <span style={{
    fontSize: 11, fontWeight: 600, color, background: `${color}18`,
    padding: "2px 8px", borderRadius: 20, border: `1px solid ${color}33`,
    whiteSpace: "nowrap",
  }}>{size}</span>
);

const TimeBadge = ({ time, color = colors.accent }) => (
  <span style={{
    fontSize: 11, fontWeight: 600, color, background: `${color}18`,
    padding: "2px 8px", borderRadius: 20, border: `1px solid ${color}33`,
    whiteSpace: "nowrap",
  }}>{time}</span>
);

const ServiceBox = ({ title, subtitle, children, color = colors.accent, width = "100%" }) => (
  <div style={{
    background: colors.surface, border: `1px solid ${color}44`,
    borderRadius: 12, padding: "16px 18px", width,
    boxShadow: `0 0 20px ${color}10, inset 0 1px 0 ${color}15`,
  }}>
    <div style={{ fontSize: 13, fontWeight: 700, color, letterSpacing: "0.03em", marginBottom: 2 }}>{title}</div>
    {subtitle && <div style={{ fontSize: 11, color: colors.textMuted, marginBottom: 10 }}>{subtitle}</div>}
    {children}
  </div>
);

const UtilBar = ({ label, percent, color, idle = false }) => (
  <div style={{ marginBottom: 6 }}>
    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 3 }}>
      <span style={{ color: idle ? colors.textMuted : colors.text, fontWeight: 500 }}>{label}</span>
      <span style={{ color: idle ? `${colors.red}aa` : color, fontWeight: 600 }}>
        {idle ? "Idle" : `${percent}%`}
      </span>
    </div>
    <div style={{ height: 6, background: "#1a2235", borderRadius: 3, overflow: "hidden" }}>
      <div style={{
        height: "100%", borderRadius: 3, width: idle ? "100%" : `${percent}%`,
        background: idle
          ? `repeating-linear-gradient(45deg, ${colors.red}20, ${colors.red}20 4px, transparent 4px, transparent 8px)`
          : color,
        transition: "width 0.8s ease",
      }} />
    </div>
  </div>
);

const S3Bucket = ({ label, size }) => (
  <div style={{
    display: "inline-flex", alignItems: "center", gap: 8,
    background: "#0d2137", border: `1px solid ${colors.accent}33`,
    borderRadius: 8, padding: "8px 14px",
  }}>
    <svg width="18" height="18" viewBox="0 0 18 18">
      <rect x="2" y="4" width="14" height="10" rx="2" fill="none" stroke={colors.accent} strokeWidth="1.5"/>
      <path d="M2 7h14" stroke={colors.accent} strokeWidth="1" opacity="0.5"/>
    </svg>
    <div>
      <div style={{ fontSize: 12, fontWeight: 600, color: colors.accent }}>{label}</div>
      {size && <div style={{ fontSize: 10, color: colors.textMuted }}>{size}</div>}
    </div>
  </div>
);

/* ── Metric cards ───────────────────────────────────────────────────── */

const PhaseMetric = ({ icon, label, current, baseline, unit, better = "lower", fmt }) => {
  const format = fmt || (v => v);
  const showComparison = baseline != null && current != null && current !== baseline;
  const improved = better === "lower" ? current < baseline : current > baseline;
  const pctChange = baseline ? Math.round(Math.abs((baseline - current) / baseline) * 100) : 0;
  return (
    <div style={{
      background: colors.surface, border: `1px solid ${colors.border}`,
      borderRadius: 12, padding: "14px 16px", flex: 1, minWidth: 130,
    }}>
      <div style={{
        fontSize: 10, color: colors.textMuted, marginBottom: 8, fontWeight: 500,
        letterSpacing: "0.04em", textTransform: "uppercase",
      }}>
        {icon} {label}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 5, marginBottom: 2 }}>
        <span style={{ fontSize: 24, fontWeight: 700, color: colors.text, fontVariantNumeric: "tabular-nums" }}>
          {current != null ? format(current) : "—"}
        </span>
        <span style={{ fontSize: 12, color: colors.textMuted }}>{unit}</span>
      </div>
      {showComparison && (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 11, color: colors.textMuted, textDecoration: "line-through" }}>
            {format(baseline)} {unit}
          </span>
          {improved && (
            <span style={{
              fontSize: 10, fontWeight: 700, color: colors.green,
              background: colors.greenGlow, padding: "1px 6px", borderRadius: 10,
            }}>
              {better === "lower" ? "↓" : "↑"} {pctChange}%
            </span>
          )}
        </div>
      )}
    </div>
  );
};

/* ── Architecture diagrams ──────────────────────────────────────────── */

const BeforeArchitecture = () => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 0 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
      <span style={{ fontSize: 20 }}>📱</span>
      <span style={{ fontSize: 13, color: colors.textMuted }}>Phone uploads video</span>
      <DataBadge size="168 MB .MOV" />
    </div>
    <Arrow />
    <S3Bucket label="S3 /raw" size="168 MB" />
    <Arrow />
    <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "2px 0" }}>
      <DataBadge size="168 MB download" /> <TimeBadge time="~15s" />
    </div>
    <Arrow />
    <ServiceBox title="AWS Lambda" subtitle="2 vCPU · CPU-only" color={colors.orange}>
      <div style={{ fontSize: 12, color: colors.text, marginBottom: 8 }}>
        CPU transcode (libx264) — HEVC → H.264
      </div>
      <UtilBar label="CPU (2 cores)" percent={100} color={colors.orange} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 6 }}>
        <TimeBadge time="⏱ 7 min" color={colors.red} />
        <span style={{ fontSize: 11, color: colors.textMuted }}>Output: 394 MB .mp4</span>
      </div>
    </ServiceBox>
    <Arrow />
    <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "2px 0" }}>
      <DataBadge size="394 MB upload" /> <TimeBadge time="~30s" />
    </div>
    <Arrow />
    <S3Bucket label="S3 /processed" size="394 MB" />
    <Arrow />
    <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "2px 0" }}>
      <DataBadge size="394 MB download" /> <TimeBadge time="~30s" />
    </div>
    <Arrow />
    <ServiceBox title="EC2 g6.2xlarge" subtitle="8 vCPU + NVIDIA L4 GPU" color={colors.purple}>
      <div style={{ fontSize: 12, color: colors.text, marginBottom: 8 }}>Pose estimation (ViTPose-Huge)</div>
      <UtilBar label="CPU — cv2 decode + preprocess" percent={100} color={colors.orange} />
      <UtilBar label="CUDA — RTMDet + ViTPose" percent={50} color={colors.purple} />
      <UtilBar label="NVENC" percent={0} color={colors.red} idle />
      <UtilBar label="NVDEC" percent={0} color={colors.red} idle />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 6 }}>
        <TimeBadge time="⏱ 10 min" color={colors.red} />
        <span style={{ fontSize: 11, color: colors.textMuted }}>Output: 1.2 MB .pkl</span>
      </div>
    </ServiceBox>
    <Arrow />
    <S3Bucket label="S3 /keypoints" size="1.2 MB" />
  </div>
);

const MergedArchitecture = ({ phase }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 0 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
      <span style={{ fontSize: 20 }}>📱</span>
      <span style={{ fontSize: 13, color: colors.textMuted }}>Phone uploads video</span>
      <DataBadge size="168 MB .MOV" />
    </div>
    <Arrow color={phase.color} />
    <S3Bucket label="S3 /raw" size="168 MB" />
    <Arrow color={phase.color} />
    <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "2px 0" }}>
      <DataBadge size="168 MB download" color={phase.color} />
      <TimeBadge time="~15s" color={phase.color} />
    </div>
    <Arrow color={phase.color} />
    <ServiceBox
      title="EC2 g6.2xlarge"
      subtitle="8 vCPU + NVIDIA L4 GPU — single service does everything"
      color={phase.color}
      width="100%"
    >
      {/* Step 1: Transcode */}
      <div style={{
        background: `${colors.green}08`, border: `1px solid ${colors.green}22`,
        borderRadius: 8, padding: 12, marginBottom: 10,
      }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: colors.green, marginBottom: 6 }}>
          Step 1 — NVENC Transcode
        </div>
        <UtilBar label="NVENC — H.264 encode" percent={85} color={colors.green} />
        <UtilBar label="CUDA" percent={0} color={colors.textMuted} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 4 }}>
          <TimeBadge time="⏱ ~24 seconds" color={colors.green} />
          <span style={{ fontSize: 11, color: colors.textMuted }}>Output: local .mp4</span>
        </div>
      </div>

      {/* Divider */}
      <div style={{
        display: "flex", justifyContent: "center", alignItems: "center", gap: 8,
        fontSize: 11, color: colors.green, fontWeight: 600, padding: "4px 0",
      }}>
        <span style={{ width: 30, height: 1, background: `${colors.green}44`, display: "inline-block" }} />
        No network transfer — file stays on local disk
        <span style={{ width: 30, height: 1, background: `${colors.green}44`, display: "inline-block" }} />
      </div>

      {/* Step 2: Labeling */}
      <div style={{
        background: `${colors.purple}08`, border: `1px solid ${colors.purple}22`,
        borderRadius: 8, padding: 12, marginTop: 10,
      }}>
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6,
        }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: colors.purple }}>
            Step 2 — Pose Estimation
          </div>
          {phase.inference !== "Eager PyTorch" && (
            <span style={{
              fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 10,
              color: colors.green, background: colors.greenGlow,
              border: `1px solid ${colors.green}33`,
            }}>
              {phase.inference}
            </span>
          )}
        </div>

        {/* Two-thread architecture detail */}
        <div style={{
          fontSize: 10, color: colors.textMuted, marginBottom: 8, padding: "6px 8px",
          background: `${colors.border}33`, borderRadius: 6, lineHeight: 1.5,
        }}>
          <span style={{ fontWeight: 600, color: colors.text }}>Two-thread overlap:</span>{" "}
          background thread ({phase.nvdecIdle ? "cv2 CPU" : "NVDEC"} decode + preprocess) stays
          ahead of main thread (GPU inference) via queue
        </div>

        {phase.nvdecIdle
          ? <UtilBar label="NVDEC" percent={0} color={colors.red} idle />
          : <UtilBar label={"NVDEC — h264_cuvid decode"} percent={40} color={colors.accent} />
        }
        <UtilBar label={`CPU — ${phase.nvdecIdle ? "cv2 decode + " : ""}preprocess`} percent={phase.cpuPct} color={colors.orange} />
        <UtilBar
          label={`CUDA — RTMDet + ViTPose${phase.inference !== "Eager PyTorch" ? " (compiled)" : ""}`}
          percent={phase.cudaPct}
          color={colors.purple}
        />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 6 }}>
          <TimeBadge time={`⏱ ${phase.labelTime} (${phase.labelFps})`} color={colors.purple} />
          <span style={{ fontSize: 11, color: colors.textMuted }}>Output: 1.2 MB .pkl</span>
        </div>

        {/* Bottleneck indicator */}
        <div style={{
          marginTop: 8, fontSize: 10, padding: "4px 8px", borderRadius: 6, lineHeight: 1.4,
          background: phase.nvdecIdle ? `${colors.orange}12` : `${colors.purple}12`,
          border: `1px solid ${phase.nvdecIdle ? colors.orange : colors.purple}22`,
          color: phase.nvdecIdle ? colors.orange : colors.purple,
        }}>
          {phase.nvdecIdle
            ? "⚠ Bottleneck: CPU decode (985ms/batch) — GPU waits ~430ms idle per batch"
            : phase.cudaPct >= 86
              ? `Bottleneck: GPU inference (${phase.inference === "Eager PyTorch" ? "494" : "344"}ms/batch) — reader finishes in 200ms, waits for GPU`
              : "Bottleneck: GPU inference — reader finishes in 200ms, waits for GPU"
          }
        </div>
      </div>
    </ServiceBox>
    <Arrow color={phase.color} />
    <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
      <S3Bucket label="S3 /keypoints" size="1.2 MB" />
      <S3Bucket label="S3 /processed" size="264 MB" />
    </div>
  </div>
);

/* ── GPU engine diagram ─────────────────────────────────────────────── */

const GPUDiagram = ({ phaseId }) => {
  const allActive = phaseId >= 2;
  return (
    <div style={{
      background: colors.surface, border: `1px solid ${colors.border}`,
      borderRadius: 14, padding: 24, marginTop: 8,
    }}>
      <div style={{ textAlign: "center", marginBottom: 16 }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: colors.text, marginBottom: 4 }}>
          NVIDIA L4 GPU — Three Independent Engines
        </div>
        <div style={{ fontSize: 12, color: colors.textMuted }}>
          Separate silicon blocks that run in parallel — using one doesn't affect the others
        </div>
      </div>
      <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
        {[
          {
            name: "NVDEC", desc: "Hardware video decoder", color: colors.accent, icon: "📥",
            usage: phaseId === 0 ? "Idle" : phaseId === 1 ? "Idle during labeling" : "Decode frames (h264_cuvid)",
            active: phaseId >= 2,
          },
          {
            name: "CUDA Cores", desc: "General compute", color: colors.purple, icon: "⚡",
            usage: phaseId === 0 ? "ViTPose (50% util)" : phaseId <= 2 ? "RTMDet + ViTPose (eager)" : "RTMDet + ViTPose (compiled)",
            active: true,
          },
          {
            name: "NVENC", desc: "Hardware video encoder", color: colors.green, icon: "📤",
            usage: phaseId === 0 ? "Idle" : "H.264 transcode (~24s)",
            active: phaseId >= 1,
          },
        ].map((unit) => (
          <div key={unit.name} style={{
            flex: "1 1 160px", maxWidth: 220,
            background: unit.active ? `${unit.color}0a` : `${colors.red}06`,
            border: `1px solid ${unit.active ? unit.color : colors.red}33`,
            borderRadius: 10, padding: "14px 16px", textAlign: "center",
            transition: "all 0.3s ease",
          }}>
            <div style={{ fontSize: 22, marginBottom: 4 }}>{unit.icon}</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: unit.active ? unit.color : colors.textMuted }}>
              {unit.name}
            </div>
            <div style={{ fontSize: 11, color: colors.textMuted, marginTop: 2 }}>{unit.desc}</div>
            <div style={{
              fontSize: 11, marginTop: 8, borderRadius: 6, padding: "4px 8px",
              color: unit.active ? unit.color : colors.red,
              background: unit.active ? `${unit.color}15` : `${colors.red}10`,
            }}>
              {unit.usage}
            </div>
          </div>
        ))}
      </div>
      <div style={{
        marginTop: 16, fontSize: 12, color: colors.textMuted, textAlign: "center",
        lineHeight: 1.6, maxWidth: 540, margin: "16px auto 0",
      }}>
        {phaseId === 0 && <>
          Only CUDA is active — NVENC and NVDEC sit <span style={{ color: colors.red }}>completely idle</span>.
          That's two dedicated ASICs you're paying for and not using.
        </>}
        {phaseId === 1 && <>
          NVENC is now active for transcoding at <span style={{ color: colors.green }}>zero additional cost</span>.
          NVDEC still sits idle during labeling — CPU cv2 handles decoding.
        </>}
        {phaseId === 2 && <>
          <span style={{ color: colors.green }}>All three engines active.</span> NVENC transcodes,
          NVDEC decodes frames during labeling, CUDA runs inference.
          Every silicon block on the die is earning its keep.
        </>}
        {phaseId === 3 && <>
          <span style={{ color: colors.green }}>All three engines active</span> with compiled CUDA kernels.
          torch.compile fuses RTMDet ops for 2.2x speedup. ViTPose (bandwidth-bound) gets 1.08x.
        </>}
      </div>
    </div>
  );
};

/* ── Gains summary ──────────────────────────────────────────────────── */

const gainSteps = [
  { num: "1", label: "NVENC replaces Lambda CPU transcode", detail: "7 min → 24 sec transcode + eliminated S3 round-trip", color: colors.orange, phase: 1 },
  { num: "2", label: "NVDEC hardware decode + threaded overlap", detail: "cv2 CPU decode (985ms/batch) → NVDEC (200ms/batch)", color: colors.accent, phase: 2 },
  { num: "3", label: "torch.compile on RTMDet + ViTPose", detail: "GPU inference 494ms → 344ms/batch (1.44x faster)", color: colors.green, phase: 3 },
];

const GainsSummary = ({ phaseId }) => (
  <div style={{
    background: colors.surface, border: `1px solid ${colors.border}`,
    borderRadius: 14, padding: 24, marginTop: 24, marginBottom: 32,
  }}>
    <div style={{ fontSize: 16, fontWeight: 700, color: colors.text, marginBottom: 14 }}>
      Where the Gains Come From
    </div>
    {gainSteps.map((item) => {
      const active = phaseId >= item.phase;
      return (
        <div key={item.num} style={{
          display: "flex", gap: 14, alignItems: "flex-start",
          padding: "12px 0", borderBottom: `1px solid ${colors.border}33`,
          opacity: active ? 1 : 0.35,
          transition: "opacity 0.3s ease",
        }}>
          <div style={{
            width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
            display: "flex", alignItems: "center", justifyContent: "center",
            background: active ? `${item.color}18` : `${colors.border}33`,
            color: active ? item.color : colors.textMuted,
            fontSize: 13, fontWeight: 700,
            border: `1px solid ${active ? item.color : colors.border}33`,
          }}>{item.num}</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: active ? colors.text : colors.textMuted }}>
              {item.label}
            </div>
            <div style={{ fontSize: 12, color: colors.textMuted, marginTop: 2 }}>{item.detail}</div>
          </div>
        </div>
      );
    })}
  </div>
);

/* ── Cost comparison ────────────────────────────────────────────────── */

const CostComparison = () => (
  <div style={{
    background: colors.surface, border: `1px solid ${colors.border}`,
    borderRadius: 14, padding: 24, marginTop: 24,
  }}>
    <div style={{ fontSize: 16, fontWeight: 700, color: colors.text, marginBottom: 16 }}>
      Why Not Keep a Separate CPU for Transcoding?
    </div>
    <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
      <div style={{
        flex: 1, minWidth: 200,
        background: colors.redGlow, border: `1px solid ${colors.red}22`,
        borderRadius: 10, padding: 16,
      }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: colors.red, marginBottom: 8 }}>
          ✗ Separate CPU (c6i.2xlarge)
        </div>
        <div style={{ fontSize: 12, color: colors.textMuted, lineHeight: 1.7 }}>
          +$0.10/hr instance cost<br/>
          +1 extra S3 round-trip (788 MB)<br/>
          +1 extra service to manage<br/>
          = <span style={{ color: colors.red }}>More money, slower results</span>
        </div>
      </div>
      <div style={{
        flex: 1, minWidth: 200,
        background: colors.greenGlow, border: `1px solid ${colors.green}22`,
        borderRadius: 10, padding: 16,
      }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: colors.green, marginBottom: 8 }}>
          ✓ NVENC on Existing GPU
        </div>
        <div style={{ fontSize: 12, color: colors.textMuted, lineHeight: 1.7 }}>
          $0.00 additional cost<br/>
          0 extra S3 transfers<br/>
          0 extra services<br/>
          = <span style={{ color: colors.green }}>Free speedup</span>
        </div>
      </div>
    </div>
  </div>
);

/* ── Main component ─────────────────────────────────────────────────── */

export default function PipelineViz() {
  const [phaseId, setPhaseId] = useState(0);
  const p = phases[phaseId];
  const base = phases[0];

  return (
    <div style={{
      fontFamily: "'IBM Plex Sans', 'SF Pro Display', -apple-system, sans-serif",
      background: colors.bg, color: colors.text,
      padding: "32px 20px",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
        * { box-sizing: border-box; }
      `}</style>
      <div style={{ maxWidth: 640, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{
            fontSize: 11, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase",
            color: colors.accent, marginBottom: 8,
          }}>Golf Swing Analysis Pipeline</div>
          <h1 style={{
            fontSize: 28, fontWeight: 700, color: colors.text,
            fontFamily: "'IBM Plex Mono', monospace", lineHeight: 1.2,
          }}>
            Three Phases: 18 min → 6 min
          </h1>
          <p style={{ fontSize: 14, color: colors.textMuted, marginTop: 8, lineHeight: 1.5 }}>
            Architecture cleanup, hardware decode, and torch.compile — each phase revealed a new bottleneck.
          </p>
        </div>

        {/* Metric cards */}
        <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
          <PhaseMetric icon="⏱" label="Wall Time" current={p.wallMin} baseline={base.wallMin} unit="min" />
          <PhaseMetric icon="⚡" label="Label FPS" current={p.fps} baseline={null} unit="fps" better="higher" />
          <PhaseMetric icon="💰" label="Cost / Video" current={p.cost} baseline={base.cost} unit="$" fmt={v => v.toFixed(2)} />
          <PhaseMetric icon="📡" label="Data Moved" current={p.dataMB} baseline={base.dataMB} unit="MB" />
        </div>

        {/* Phase selector */}
        <div style={{
          display: "flex", background: colors.surface, borderRadius: 10,
          border: `1px solid ${colors.border}`, padding: 4, marginBottom: 24,
          gap: 3,
        }}>
          {phases.map((ph) => (
            <button key={ph.id} onClick={() => setPhaseId(ph.id)} style={{
              flex: 1, padding: "8px 6px", borderRadius: 7,
              border: "none", cursor: "pointer", fontWeight: 600, fontSize: 11,
              fontFamily: "inherit", letterSpacing: "0.01em", transition: "all 0.2s",
              background: phaseId === ph.id ? `${ph.color}20` : "transparent",
              color: phaseId === ph.id ? ph.color : colors.textMuted,
              boxShadow: phaseId === ph.id ? `0 0 12px ${ph.glow}` : "none",
              display: "flex", flexDirection: "column", alignItems: "center", gap: 2,
            }}>
              <span>{ph.label}</span>
              <span style={{
                fontSize: 10, fontWeight: 700, opacity: 0.8,
              }}>{ph.time}</span>
            </button>
          ))}
        </div>

        {/* Architecture diagram */}
        <div style={{
          background: `${colors.bg}cc`, border: `1px solid ${colors.border}`,
          borderRadius: 14, padding: "24px 20px",
        }}>
          <div style={{
            display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16,
          }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: p.color }}>
                {p.title}
              </div>
              <div style={{ fontSize: 12, color: colors.textMuted, marginTop: 2 }}>
                {p.subtitle}
              </div>
            </div>
            <div style={{
              fontSize: 11, fontWeight: 600, padding: "4px 10px", borderRadius: 20,
              color: p.color, background: p.glow,
              border: `1px solid ${p.color}33`,
            }}>
              {p.time}
            </div>
          </div>
          {phaseId === 0 ? <BeforeArchitecture /> : <MergedArchitecture phase={p} />}
        </div>

        {/* GPU engine diagram */}
        <div style={{ marginTop: 24 }}>
          <GPUDiagram phaseId={phaseId} />
        </div>

        {/* Cost comparison */}
        <CostComparison />

        {/* Gains summary */}
        <GainsSummary phaseId={phaseId} />
      </div>
    </div>
  );
}

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
  purple: "#a78bfa",
};

const Arrow = ({ color = colors.textMuted, style = {} }) => (
  <div style={{ display: "flex", justifyContent: "center", padding: "4px 0", ...style }}>
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
        background: idle ? `repeating-linear-gradient(45deg, ${colors.red}20, ${colors.red}20 4px, transparent 4px, transparent 8px)` : color,
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

const MetricCard = ({ label, before, after, unit = "", better = "lower", icon }) => {
  const improved = better === "lower" ? after < before : after > before;
  const pctChange = Math.round(((before - after) / before) * 100);
  return (
    <div style={{
      background: colors.surface, border: `1px solid ${colors.border}`,
      borderRadius: 12, padding: "16px 18px", flex: 1, minWidth: 150,
    }}>
      <div style={{ fontSize: 11, color: colors.textMuted, marginBottom: 10, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>
        {icon} {label}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 6, marginBottom: 2 }}>
        <span style={{ fontSize: 26, fontWeight: 700, color: colors.text, fontVariantNumeric: "tabular-nums" }}>{after}</span>
        <span style={{ fontSize: 13, color: colors.textMuted }}>{unit}</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span style={{ fontSize: 12, color: colors.textMuted, textDecoration: "line-through" }}>{before} {unit}</span>
        {improved && (
          <span style={{
            fontSize: 11, fontWeight: 700, color: colors.green,
            background: colors.greenGlow, padding: "1px 7px", borderRadius: 10,
          }}>↓ {pctChange}%</span>
        )}
      </div>
    </div>
  );
};

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
      <div style={{ fontSize: 12, color: colors.text, marginBottom: 8 }}>Pose estimation (ViTPose)</div>
      <UtilBar label="CPU — cv2 decode + preprocess" percent={100} color={colors.orange} />
      <UtilBar label="CUDA — ViTPose" percent={16} color={colors.purple} />
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

const AfterArchitecture = () => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 0 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
      <span style={{ fontSize: 20 }}>📱</span>
      <span style={{ fontSize: 13, color: colors.textMuted }}>Phone uploads video</span>
      <DataBadge size="168 MB .MOV" />
    </div>
    <Arrow color={colors.green} />
    <S3Bucket label="S3 /raw" size="168 MB" />
    <Arrow color={colors.green} />
    <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "2px 0" }}>
      <DataBadge size="168 MB download" color={colors.green} /> <TimeBadge time="~15s" color={colors.green} />
    </div>
    <Arrow color={colors.green} />
    <ServiceBox title="EC2 g6.2xlarge" subtitle="8 vCPU + NVIDIA L4 GPU · Single service does everything" color={colors.green} width="100%">
      <div style={{
        background: `${colors.green}08`, border: `1px solid ${colors.green}22`,
        borderRadius: 8, padding: 12, marginBottom: 10,
      }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: colors.green, marginBottom: 6 }}>
          Step 1 — GPU Transcode
        </div>
        <UtilBar label="CPU — decode HEVC 10-bit → 8-bit" percent={70} color={colors.accent} />
        <UtilBar label="NVENC — encode H.264" percent={85} color={colors.green} />
        <UtilBar label="CUDA" percent={0} color={colors.textMuted} idle={false} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 4 }}>
          <TimeBadge time="⏱ 36 seconds" color={colors.green} />
          <span style={{ fontSize: 11, color: colors.textMuted }}>Output: local .mp4</span>
        </div>
      </div>
      <div style={{
        display: "flex", justifyContent: "center", alignItems: "center", gap: 8,
        fontSize: 11, color: colors.green, fontWeight: 600, padding: "4px 0",
      }}>
        <span style={{ width: 30, height: 1, background: `${colors.green}44`, display: "inline-block" }} />
        No network transfer — file stays on local disk
        <span style={{ width: 30, height: 1, background: `${colors.green}44`, display: "inline-block" }} />
      </div>
      <div style={{
        background: `${colors.purple}08`, border: `1px solid ${colors.purple}22`,
        borderRadius: 8, padding: 12, marginTop: 10,
      }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: colors.purple, marginBottom: 6 }}>
          Step 2 — Pose Estimation
        </div>
        <UtilBar label="CPU — cv2 decode + preprocess" percent={100} color={colors.orange} />
        <UtilBar label="CUDA — ViTPose inference" percent={80} color={colors.purple} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 4 }}>
          <TimeBadge time="⏱ ~10 min (2.8 min w/ NVDEC)" color={colors.purple} />
          <span style={{ fontSize: 11, color: colors.textMuted }}>Output: 1.2 MB .pkl + 264 MB .mp4</span>
        </div>
      </div>
    </ServiceBox>
    <Arrow color={colors.green} />
    <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
      <S3Bucket label="S3 /keypoints" size="1.2 MB" />
      <S3Bucket label="S3 /processed" size="264 MB" />
    </div>
  </div>
);

const GPUDiagram = () => (
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
        { name: "NVDEC", desc: "Hardware video decoder", usage: "Phase 2: decode frames", color: colors.accent, icon: "📥" },
        { name: "CUDA Cores", desc: "General compute", usage: "ViTPose inference", color: colors.purple, icon: "⚡" },
        { name: "NVENC", desc: "Hardware video encoder", usage: "Phase 1: H.264 transcode", color: colors.green, icon: "📤" },
      ].map((unit) => (
        <div key={unit.name} style={{
          flex: "1 1 160px", maxWidth: 220,
          background: `${unit.color}0a`, border: `1px solid ${unit.color}33`,
          borderRadius: 10, padding: "14px 16px", textAlign: "center",
        }}>
          <div style={{ fontSize: 22, marginBottom: 4 }}>{unit.icon}</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: unit.color }}>{unit.name}</div>
          <div style={{ fontSize: 11, color: colors.textMuted, marginTop: 2 }}>{unit.desc}</div>
          <div style={{
            fontSize: 11, color: unit.color, marginTop: 8,
            background: `${unit.color}15`, borderRadius: 6, padding: "4px 8px",
          }}>{unit.usage}</div>
        </div>
      ))}
    </div>
    <div style={{
      marginTop: 16, fontSize: 12, color: colors.textMuted, textAlign: "center",
      lineHeight: 1.6, maxWidth: 520, margin: "16px auto 0",
    }}>
      Before the merge, only CUDA was used — NVENC and NVDEC sat <span style={{ color: colors.red }}>completely idle</span>.
      {" "}The merged architecture activates NVENC for transcoding at <span style={{ color: colors.green }}>zero additional cost</span> because
      {" "}it's dedicated hardware on an instance you're already paying for.
    </div>
  </div>
);

export default function PipelineViz() {
  const [view, setView] = useState("before");

  return (
    <div style={{
      fontFamily: "'IBM Plex Sans', 'SF Pro Display', -apple-system, sans-serif",
      background: colors.bg, color: colors.text, minHeight: "100vh",
      padding: "32px 20px",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: ${colors.bg}; }
      `}</style>
      <div style={{ maxWidth: 640, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            fontSize: 11, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase",
            color: colors.accent, marginBottom: 8,
          }}>Golf Swing Analysis Pipeline</div>
          <h1 style={{
            fontSize: 28, fontWeight: 700, color: colors.text,
            fontFamily: "'IBM Plex Mono', monospace", lineHeight: 1.2,
          }}>
            Data Flow: Before & After
          </h1>
          <p style={{ fontSize: 14, color: colors.textMuted, marginTop: 8, lineHeight: 1.5 }}>
            Merging Lambda + EC2 into a single EC2 service — cutting time, transfers, and cost.
          </p>
        </div>

        {/* Summary metrics */}
        <div style={{ display: "flex", gap: 10, marginBottom: 28, flexWrap: "wrap" }}>
          <MetricCard icon="⏱" label="Wall Time" before={18} after={12} unit="min" />
          <MetricCard icon="📡" label="Data Moved" before={957} after={433} unit="MB" />
          <MetricCard icon="🔧" label="Services" before={2} after={1} unit="" />
        </div>

        {/* Toggle */}
        <div style={{
          display: "flex", background: colors.surface, borderRadius: 10,
          border: `1px solid ${colors.border}`, padding: 4, marginBottom: 24,
        }}>
          {["before", "after"].map((v) => (
            <button key={v} onClick={() => setView(v)} style={{
              flex: 1, padding: "10px 16px", borderRadius: 7,
              border: "none", cursor: "pointer", fontWeight: 600, fontSize: 13,
              fontFamily: "inherit", letterSpacing: "0.02em", transition: "all 0.2s",
              background: view === v
                ? (v === "before" ? `${colors.red}20` : `${colors.green}20`)
                : "transparent",
              color: view === v
                ? (v === "before" ? colors.red : colors.green)
                : colors.textMuted,
              boxShadow: view === v
                ? `0 0 12px ${v === "before" ? colors.redGlow : colors.greenGlow}`
                : "none",
            }}>
              {v === "before" ? "⬅ Before: Lambda + EC2" : "After: EC2 Only ➡"}
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
              <div style={{
                fontSize: 14, fontWeight: 700, color: view === "before" ? colors.red : colors.green,
              }}>
                {view === "before" ? "Two-Service Architecture" : "Single-Service Architecture"}
              </div>
              <div style={{ fontSize: 12, color: colors.textMuted, marginTop: 2 }}>
                {view === "before"
                  ? "Video crosses the network 3 times through 2 services"
                  : "Video crosses the network once — everything on one machine"
                }
              </div>
            </div>
            <div style={{
              fontSize: 11, fontWeight: 600, padding: "4px 10px", borderRadius: 20,
              color: view === "before" ? colors.red : colors.green,
              background: view === "before" ? colors.redGlow : colors.greenGlow,
              border: `1px solid ${view === "before" ? `${colors.red}33` : `${colors.green}33`}`,
            }}>
              {view === "before" ? "~18 min" : "~12 min"}
            </div>
          </div>
          {view === "before" ? <BeforeArchitecture /> : <AfterArchitecture />}
        </div>

        {/* GPU Explanation */}
        <div style={{ marginTop: 24 }}>
          <GPUDiagram />
        </div>

        {/* Cost comparison */}
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

        {/* Efficiency gains */}
        <div style={{
          background: colors.surface, border: `1px solid ${colors.border}`,
          borderRadius: 14, padding: 24, marginTop: 24, marginBottom: 32,
        }}>
          <div style={{ fontSize: 16, fontWeight: 700, color: colors.text, marginBottom: 14 }}>
            Where the Gains Come From
          </div>
          {[
            { num: "1", label: "Eliminate the intermediate S3 hop", detail: "Saves ~1 min + 394 MB transfer", color: colors.accent },
            { num: "2", label: "NVENC replaces CPU transcode", detail: "7 min → 36 sec (saves ~6.5 min)", color: colors.green },
            { num: "3", label: "File stays local between steps", detail: "Saves ~30s download between transcode & labeling", color: colors.purple },
          ].map((item) => (
            <div key={item.num} style={{
              display: "flex", gap: 14, alignItems: "flex-start",
              padding: "12px 0", borderBottom: `1px solid ${colors.border}33`,
            }}>
              <div style={{
                width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                background: `${item.color}18`, color: item.color,
                fontSize: 13, fontWeight: 700, border: `1px solid ${item.color}33`,
              }}>{item.num}</div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: colors.text }}>{item.label}</div>
                <div style={{ fontSize: 12, color: colors.textMuted, marginTop: 2 }}>{item.detail}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const { useState } = React;
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
  purple: "#a78bfa"
};
const Arrow = ({
  color = colors.textMuted,
  style = {}
}) => /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    justifyContent: "center",
    padding: "4px 0",
    ...style
  }
}, /*#__PURE__*/React.createElement("svg", {
  width: "20",
  height: "28",
  viewBox: "0 0 20 28"
}, /*#__PURE__*/React.createElement("line", {
  x1: "10",
  y1: "0",
  x2: "10",
  y2: "22",
  stroke: color,
  strokeWidth: "2",
  strokeDasharray: "4,3"
}), /*#__PURE__*/React.createElement("polygon", {
  points: "4,20 10,28 16,20",
  fill: color
})));
const DataBadge = ({
  size,
  color = colors.orange
}) => /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 11,
    fontWeight: 600,
    color,
    background: `${color}18`,
    padding: "2px 8px",
    borderRadius: 20,
    border: `1px solid ${color}33`,
    whiteSpace: "nowrap"
  }
}, size);
const TimeBadge = ({
  time,
  color = colors.accent
}) => /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 11,
    fontWeight: 600,
    color,
    background: `${color}18`,
    padding: "2px 8px",
    borderRadius: 20,
    border: `1px solid ${color}33`,
    whiteSpace: "nowrap"
  }
}, time);
const ServiceBox = ({
  title,
  subtitle,
  children,
  color = colors.accent,
  width = "100%"
}) => /*#__PURE__*/React.createElement("div", {
  style: {
    background: colors.surface,
    border: `1px solid ${color}44`,
    borderRadius: 12,
    padding: "16px 18px",
    width,
    boxShadow: `0 0 20px ${color}10, inset 0 1px 0 ${color}15`
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 13,
    fontWeight: 700,
    color,
    letterSpacing: "0.03em",
    marginBottom: 2
  }
}, title), subtitle && /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 11,
    color: colors.textMuted,
    marginBottom: 10
  }
}, subtitle), children);
const UtilBar = ({
  label,
  percent,
  color,
  idle = false
}) => /*#__PURE__*/React.createElement("div", {
  style: {
    marginBottom: 6
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: 11,
    marginBottom: 3
  }
}, /*#__PURE__*/React.createElement("span", {
  style: {
    color: idle ? colors.textMuted : colors.text,
    fontWeight: 500
  }
}, label), /*#__PURE__*/React.createElement("span", {
  style: {
    color: idle ? `${colors.red}aa` : color,
    fontWeight: 600
  }
}, idle ? "Idle" : `${percent}%`)), /*#__PURE__*/React.createElement("div", {
  style: {
    height: 6,
    background: "#1a2235",
    borderRadius: 3,
    overflow: "hidden"
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    height: "100%",
    borderRadius: 3,
    width: idle ? "100%" : `${percent}%`,
    background: idle ? `repeating-linear-gradient(45deg, ${colors.red}20, ${colors.red}20 4px, transparent 4px, transparent 8px)` : color,
    transition: "width 0.8s ease"
  }
})));
const S3Bucket = ({
  label,
  size
}) => /*#__PURE__*/React.createElement("div", {
  style: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    background: "#0d2137",
    border: `1px solid ${colors.accent}33`,
    borderRadius: 8,
    padding: "8px 14px"
  }
}, /*#__PURE__*/React.createElement("svg", {
  width: "18",
  height: "18",
  viewBox: "0 0 18 18"
}, /*#__PURE__*/React.createElement("rect", {
  x: "2",
  y: "4",
  width: "14",
  height: "10",
  rx: "2",
  fill: "none",
  stroke: colors.accent,
  strokeWidth: "1.5"
}), /*#__PURE__*/React.createElement("path", {
  d: "M2 7h14",
  stroke: colors.accent,
  strokeWidth: "1",
  opacity: "0.5"
})), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 12,
    fontWeight: 600,
    color: colors.accent
  }
}, label), size && /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 10,
    color: colors.textMuted
  }
}, size)));
const MetricCard = ({
  label,
  before,
  after,
  unit = "",
  better = "lower",
  icon
}) => {
  const improved = better === "lower" ? after < before : after > before;
  const pctChange = Math.round((before - after) / before * 100);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: colors.surface,
      border: `1px solid ${colors.border}`,
      borderRadius: 12,
      padding: "16px 18px",
      flex: 1,
      minWidth: 150
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: colors.textMuted,
      marginBottom: 10,
      fontWeight: 500,
      letterSpacing: "0.04em",
      textTransform: "uppercase"
    }
  }, icon, " ", label), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "baseline",
      gap: 6,
      marginBottom: 2
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 26,
      fontWeight: 700,
      color: colors.text,
      fontVariantNumeric: "tabular-nums"
    }
  }, after), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      color: colors.textMuted
    }
  }, unit)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: colors.textMuted,
      textDecoration: "line-through"
    }
  }, before, " ", unit), improved && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 11,
      fontWeight: 700,
      color: colors.green,
      background: colors.greenGlow,
      padding: "1px 7px",
      borderRadius: 10
    }
  }, "\u2193 ", pctChange, "%")));
};
const BeforeArchitecture = () => /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 0
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginBottom: 2
  }
}, /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 20
  }
}, "\uD83D\uDCF1"), /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 13,
    color: colors.textMuted
  }
}, "Phone uploads video"), /*#__PURE__*/React.createElement(DataBadge, {
  size: "168 MB .MOV"
})), /*#__PURE__*/React.createElement(Arrow, null), /*#__PURE__*/React.createElement(S3Bucket, {
  label: "S3 /raw",
  size: "168 MB"
}), /*#__PURE__*/React.createElement(Arrow, null), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "2px 0"
  }
}, /*#__PURE__*/React.createElement(DataBadge, {
  size: "168 MB download"
}), " ", /*#__PURE__*/React.createElement(TimeBadge, {
  time: "~15s"
})), /*#__PURE__*/React.createElement(Arrow, null), /*#__PURE__*/React.createElement(ServiceBox, {
  title: "AWS Lambda",
  subtitle: "2 vCPU \xB7 CPU-only",
  color: colors.orange
}, /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 12,
    color: colors.text,
    marginBottom: 8
  }
}, "CPU transcode (libx264) \u2014 HEVC \u2192 H.264"), /*#__PURE__*/React.createElement(UtilBar, {
  label: "CPU (2 cores)",
  percent: 100,
  color: colors.orange
}), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 6
  }
}, /*#__PURE__*/React.createElement(TimeBadge, {
  time: "\u23F1 7 min",
  color: colors.red
}), /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 11,
    color: colors.textMuted
  }
}, "Output: 394 MB .mp4"))), /*#__PURE__*/React.createElement(Arrow, null), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "2px 0"
  }
}, /*#__PURE__*/React.createElement(DataBadge, {
  size: "394 MB upload"
}), " ", /*#__PURE__*/React.createElement(TimeBadge, {
  time: "~30s"
})), /*#__PURE__*/React.createElement(Arrow, null), /*#__PURE__*/React.createElement(S3Bucket, {
  label: "S3 /processed",
  size: "394 MB"
}), /*#__PURE__*/React.createElement(Arrow, null), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "2px 0"
  }
}, /*#__PURE__*/React.createElement(DataBadge, {
  size: "394 MB download"
}), " ", /*#__PURE__*/React.createElement(TimeBadge, {
  time: "~30s"
})), /*#__PURE__*/React.createElement(Arrow, null), /*#__PURE__*/React.createElement(ServiceBox, {
  title: "EC2 g6.2xlarge",
  subtitle: "8 vCPU + NVIDIA L4 GPU",
  color: colors.purple
}, /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 12,
    color: colors.text,
    marginBottom: 8
  }
}, "Pose estimation (ViTPose)"), /*#__PURE__*/React.createElement(UtilBar, {
  label: "CPU \u2014 cv2 decode + preprocess",
  percent: 100,
  color: colors.orange
}), /*#__PURE__*/React.createElement(UtilBar, {
  label: "CUDA \u2014 ViTPose",
  percent: 16,
  color: colors.purple
}), /*#__PURE__*/React.createElement(UtilBar, {
  label: "NVENC",
  percent: 0,
  color: colors.red,
  idle: true
}), /*#__PURE__*/React.createElement(UtilBar, {
  label: "NVDEC",
  percent: 0,
  color: colors.red,
  idle: true
}), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 6
  }
}, /*#__PURE__*/React.createElement(TimeBadge, {
  time: "\u23F1 10 min",
  color: colors.red
}), /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 11,
    color: colors.textMuted
  }
}, "Output: 1.2 MB .pkl"))), /*#__PURE__*/React.createElement(Arrow, null), /*#__PURE__*/React.createElement(S3Bucket, {
  label: "S3 /keypoints",
  size: "1.2 MB"
}));
const AfterArchitecture = () => /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 0
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginBottom: 2
  }
}, /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 20
  }
}, "\uD83D\uDCF1"), /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 13,
    color: colors.textMuted
  }
}, "Phone uploads video"), /*#__PURE__*/React.createElement(DataBadge, {
  size: "168 MB .MOV"
})), /*#__PURE__*/React.createElement(Arrow, {
  color: colors.green
}), /*#__PURE__*/React.createElement(S3Bucket, {
  label: "S3 /raw",
  size: "168 MB"
}), /*#__PURE__*/React.createElement(Arrow, {
  color: colors.green
}), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "2px 0"
  }
}, /*#__PURE__*/React.createElement(DataBadge, {
  size: "168 MB download",
  color: colors.green
}), " ", /*#__PURE__*/React.createElement(TimeBadge, {
  time: "~15s",
  color: colors.green
})), /*#__PURE__*/React.createElement(Arrow, {
  color: colors.green
}), /*#__PURE__*/React.createElement(ServiceBox, {
  title: "EC2 g6.2xlarge",
  subtitle: "8 vCPU + NVIDIA L4 GPU \xB7 Single service does everything",
  color: colors.green,
  width: "100%"
}, /*#__PURE__*/React.createElement("div", {
  style: {
    background: `${colors.green}08`,
    border: `1px solid ${colors.green}22`,
    borderRadius: 8,
    padding: 12,
    marginBottom: 10
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 12,
    fontWeight: 600,
    color: colors.green,
    marginBottom: 6
  }
}, "Step 1 \u2014 GPU Transcode"), /*#__PURE__*/React.createElement(UtilBar, {
  label: "CPU \u2014 decode HEVC 10-bit \u2192 8-bit",
  percent: 70,
  color: colors.accent
}), /*#__PURE__*/React.createElement(UtilBar, {
  label: "NVENC \u2014 encode H.264",
  percent: 85,
  color: colors.green
}), /*#__PURE__*/React.createElement(UtilBar, {
  label: "CUDA",
  percent: 0,
  color: colors.textMuted,
  idle: false
}), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 4
  }
}, /*#__PURE__*/React.createElement(TimeBadge, {
  time: "\u23F1 36 seconds",
  color: colors.green
}), /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 11,
    color: colors.textMuted
  }
}, "Output: local .mp4"))), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    gap: 8,
    fontSize: 11,
    color: colors.green,
    fontWeight: 600,
    padding: "4px 0"
  }
}, /*#__PURE__*/React.createElement("span", {
  style: {
    width: 30,
    height: 1,
    background: `${colors.green}44`,
    display: "inline-block"
  }
}), "No network transfer \u2014 file stays on local disk", /*#__PURE__*/React.createElement("span", {
  style: {
    width: 30,
    height: 1,
    background: `${colors.green}44`,
    display: "inline-block"
  }
})), /*#__PURE__*/React.createElement("div", {
  style: {
    background: `${colors.purple}08`,
    border: `1px solid ${colors.purple}22`,
    borderRadius: 8,
    padding: 12,
    marginTop: 10
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 12,
    fontWeight: 600,
    color: colors.purple,
    marginBottom: 6
  }
}, "Step 2 \u2014 Pose Estimation"), /*#__PURE__*/React.createElement(UtilBar, {
  label: "CPU \u2014 cv2 decode + preprocess",
  percent: 100,
  color: colors.orange
}), /*#__PURE__*/React.createElement(UtilBar, {
  label: "CUDA \u2014 ViTPose inference",
  percent: 80,
  color: colors.purple
}), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 4
  }
}, /*#__PURE__*/React.createElement(TimeBadge, {
  time: "\u23F1 ~10 min (2.8 min w/ NVDEC)",
  color: colors.purple
}), /*#__PURE__*/React.createElement("span", {
  style: {
    fontSize: 11,
    color: colors.textMuted
  }
}, "Output: 1.2 MB .pkl + 264 MB .mp4")))), /*#__PURE__*/React.createElement(Arrow, {
  color: colors.green
}), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    gap: 12,
    justifyContent: "center"
  }
}, /*#__PURE__*/React.createElement(S3Bucket, {
  label: "S3 /keypoints",
  size: "1.2 MB"
}), /*#__PURE__*/React.createElement(S3Bucket, {
  label: "S3 /processed",
  size: "264 MB"
})));
const GPUDiagram = () => /*#__PURE__*/React.createElement("div", {
  style: {
    background: colors.surface,
    border: `1px solid ${colors.border}`,
    borderRadius: 14,
    padding: 24,
    marginTop: 8
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    textAlign: "center",
    marginBottom: 16
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 16,
    fontWeight: 700,
    color: colors.text,
    marginBottom: 4
  }
}, "NVIDIA L4 GPU \u2014 Three Independent Engines"), /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 12,
    color: colors.textMuted
  }
}, "Separate silicon blocks that run in parallel \u2014 using one doesn't affect the others")), /*#__PURE__*/React.createElement("div", {
  style: {
    display: "flex",
    gap: 12,
    justifyContent: "center",
    flexWrap: "wrap"
  }
}, [{
  name: "NVDEC",
  desc: "Hardware video decoder",
  usage: "Phase 2: decode frames",
  color: colors.accent,
  icon: "📥"
}, {
  name: "CUDA Cores",
  desc: "General compute",
  usage: "ViTPose inference",
  color: colors.purple,
  icon: "⚡"
}, {
  name: "NVENC",
  desc: "Hardware video encoder",
  usage: "Phase 1: H.264 transcode",
  color: colors.green,
  icon: "📤"
}].map(unit => /*#__PURE__*/React.createElement("div", {
  key: unit.name,
  style: {
    flex: "1 1 160px",
    maxWidth: 220,
    background: `${unit.color}0a`,
    border: `1px solid ${unit.color}33`,
    borderRadius: 10,
    padding: "14px 16px",
    textAlign: "center"
  }
}, /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 22,
    marginBottom: 4
  }
}, unit.icon), /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 14,
    fontWeight: 700,
    color: unit.color
  }
}, unit.name), /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 11,
    color: colors.textMuted,
    marginTop: 2
  }
}, unit.desc), /*#__PURE__*/React.createElement("div", {
  style: {
    fontSize: 11,
    color: unit.color,
    marginTop: 8,
    background: `${unit.color}15`,
    borderRadius: 6,
    padding: "4px 8px"
  }
}, unit.usage)))), /*#__PURE__*/React.createElement("div", {
  style: {
    marginTop: 16,
    fontSize: 12,
    color: colors.textMuted,
    textAlign: "center",
    lineHeight: 1.6,
    maxWidth: 520,
    margin: "16px auto 0"
  }
}, "Before the merge, only CUDA was used \u2014 NVENC and NVDEC sat ", /*#__PURE__*/React.createElement("span", {
  style: {
    color: colors.red
  }
}, "completely idle"), ".", " ", "The merged architecture activates NVENC for transcoding at ", /*#__PURE__*/React.createElement("span", {
  style: {
    color: colors.green
  }
}, "zero additional cost"), " because", " ", "it's dedicated hardware on an instance you're already paying for."));
function PipelineViz() {
  const [view, setView] = useState("before");
  return /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: "'IBM Plex Sans', 'SF Pro Display', -apple-system, sans-serif",
      background: colors.bg,
      color: colors.text,
      borderRadius: 16,
      padding: "32px 20px"
    }
  }, /*#__PURE__*/React.createElement("style", null, `
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
        #pipeline-viz-root * { box-sizing: border-box; }
      `), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 640,
      margin: "0 auto"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: "center",
      marginBottom: 32
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      fontWeight: 600,
      letterSpacing: "0.12em",
      textTransform: "uppercase",
      color: colors.accent,
      marginBottom: 8
    }
  }, "Golf Swing Analysis Pipeline"), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontSize: 28,
      fontWeight: 700,
      color: colors.text,
      fontFamily: "'IBM Plex Mono', monospace",
      lineHeight: 1.2
    }
  }, "Data Flow: Before & After"), /*#__PURE__*/React.createElement("p", {
    style: {
      fontSize: 14,
      color: colors.textMuted,
      marginTop: 8,
      lineHeight: 1.5
    }
  }, "Merging Lambda + EC2 into a single EC2 service \u2014 cutting time, transfers, and cost.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: 10,
      marginBottom: 28,
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement(MetricCard, {
    icon: "\u23F1",
    label: "Wall Time",
    before: 18,
    after: 12,
    unit: "min"
  }), /*#__PURE__*/React.createElement(MetricCard, {
    icon: "\uD83D\uDCE1",
    label: "Data Moved",
    before: 957,
    after: 433,
    unit: "MB"
  }), /*#__PURE__*/React.createElement(MetricCard, {
    icon: "\uD83D\uDD27",
    label: "Services",
    before: 2,
    after: 1,
    unit: ""
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      background: colors.surface,
      borderRadius: 10,
      border: `1px solid ${colors.border}`,
      padding: 4,
      marginBottom: 24
    }
  }, ["before", "after"].map(v => /*#__PURE__*/React.createElement("button", {
    key: v,
    onClick: () => setView(v),
    style: {
      flex: 1,
      padding: "10px 16px",
      borderRadius: 7,
      border: "none",
      cursor: "pointer",
      fontWeight: 600,
      fontSize: 13,
      fontFamily: "inherit",
      letterSpacing: "0.02em",
      transition: "all 0.2s",
      background: view === v ? v === "before" ? `${colors.red}20` : `${colors.green}20` : "transparent",
      color: view === v ? v === "before" ? colors.red : colors.green : colors.textMuted,
      boxShadow: view === v ? `0 0 12px ${v === "before" ? colors.redGlow : colors.greenGlow}` : "none"
    }
  }, v === "before" ? "⬅ Before: Lambda + EC2" : "After: EC2 Only ➡"))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: `${colors.bg}cc`,
      border: `1px solid ${colors.border}`,
      borderRadius: 14,
      padding: "24px 20px"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: 16
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 14,
      fontWeight: 700,
      color: view === "before" ? colors.red : colors.green
    }
  }, view === "before" ? "Two-Service Architecture" : "Single-Service Architecture"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: colors.textMuted,
      marginTop: 2
    }
  }, view === "before" ? "Video crosses the network 3 times through 2 services" : "Video crosses the network once — everything on one machine")), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      fontWeight: 600,
      padding: "4px 10px",
      borderRadius: 20,
      color: view === "before" ? colors.red : colors.green,
      background: view === "before" ? colors.redGlow : colors.greenGlow,
      border: `1px solid ${view === "before" ? `${colors.red}33` : `${colors.green}33`}`
    }
  }, view === "before" ? "~18 min" : "~12 min")), view === "before" ? /*#__PURE__*/React.createElement(BeforeArchitecture, null) : /*#__PURE__*/React.createElement(AfterArchitecture, null)), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 24
    }
  }, /*#__PURE__*/React.createElement(GPUDiagram, null)), /*#__PURE__*/React.createElement("div", {
    style: {
      background: colors.surface,
      border: `1px solid ${colors.border}`,
      borderRadius: 14,
      padding: 24,
      marginTop: 24
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 16,
      fontWeight: 700,
      color: colors.text,
      marginBottom: 16
    }
  }, "Why Not Keep a Separate CPU for Transcoding?"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: 12,
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 200,
      background: colors.redGlow,
      border: `1px solid ${colors.red}22`,
      borderRadius: 10,
      padding: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontWeight: 700,
      color: colors.red,
      marginBottom: 8
    }
  }, "\u2717 Separate CPU (c6i.2xlarge)"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: colors.textMuted,
      lineHeight: 1.7
    }
  }, "+$0.10/hr instance cost", /*#__PURE__*/React.createElement("br", null), "+1 extra S3 round-trip (788 MB)", /*#__PURE__*/React.createElement("br", null), "+1 extra service to manage", /*#__PURE__*/React.createElement("br", null), "= ", /*#__PURE__*/React.createElement("span", {
    style: {
      color: colors.red
    }
  }, "More money, slower results"))), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 200,
      background: colors.greenGlow,
      border: `1px solid ${colors.green}22`,
      borderRadius: 10,
      padding: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontWeight: 700,
      color: colors.green,
      marginBottom: 8
    }
  }, "\u2713 NVENC on Existing GPU"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: colors.textMuted,
      lineHeight: 1.7
    }
  }, "$0.00 additional cost", /*#__PURE__*/React.createElement("br", null), "0 extra S3 transfers", /*#__PURE__*/React.createElement("br", null), "0 extra services", /*#__PURE__*/React.createElement("br", null), "= ", /*#__PURE__*/React.createElement("span", {
    style: {
      color: colors.green
    }
  }, "Free speedup"))))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: colors.surface,
      border: `1px solid ${colors.border}`,
      borderRadius: 14,
      padding: 24,
      marginTop: 24,
      marginBottom: 32
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 16,
      fontWeight: 700,
      color: colors.text,
      marginBottom: 14
    }
  }, "Where the Gains Come From"), [{
    num: "1",
    label: "Eliminate the intermediate S3 hop",
    detail: "Saves ~1 min + 394 MB transfer",
    color: colors.accent
  }, {
    num: "2",
    label: "NVENC replaces CPU transcode",
    detail: "7 min → 36 sec (saves ~6.5 min)",
    color: colors.green
  }, {
    num: "3",
    label: "File stays local between steps",
    detail: "Saves ~30s download between transcode & labeling",
    color: colors.purple
  }].map(item => /*#__PURE__*/React.createElement("div", {
    key: item.num,
    style: {
      display: "flex",
      gap: 14,
      alignItems: "flex-start",
      padding: "12px 0",
      borderBottom: `1px solid ${colors.border}33`
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 28,
      height: 28,
      borderRadius: "50%",
      flexShrink: 0,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: `${item.color}18`,
      color: item.color,
      fontSize: 13,
      fontWeight: 700,
      border: `1px solid ${item.color}33`
    }
  }, item.num), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontWeight: 600,
      color: colors.text
    }
  }, item.label), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: colors.textMuted,
      marginTop: 2
    }
  }, item.detail)))))));
}

// Mount
const root = ReactDOM.createRoot(document.getElementById("pipeline-viz-root"));
root.render(React.createElement(PipelineViz, null));

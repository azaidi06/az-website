import React from 'react';

const Node = ({ title, subtitle, details, type = 'default', children }) => {
  const bgColors = {
    default: 'bg-white',
    aws: 'bg-orange-50',
    ec2: 'bg-purple-50',
    lambda: 'bg-orange-100',
    s3: 'bg-green-50',
    sqs: 'bg-pink-50',
    db: 'bg-blue-50',
  };

  const borderColors = {
    default: 'border-gray-300',
    aws: 'border-orange-300',
    ec2: 'border-purple-300',
    lambda: 'border-orange-400',
    s3: 'border-green-300',
    sqs: 'border-pink-300',
    db: 'border-blue-300',
  };

  return (
    <div className={`border-2 ${borderColors[type]} ${bgColors[type]} rounded-lg p-4 shadow-sm flex flex-col items-center text-center w-72 m-2 relative z-10`}>
      <h3 className="font-bold text-gray-800">{title}</h3>
      {subtitle && <p className="text-sm font-semibold text-gray-600 mt-1">{subtitle}</p>}
      {details && <p className="text-xs text-gray-500 mt-2 whitespace-pre-line">{details}</p>}
      {children && <div className="mt-3 w-full">{children}</div>}
    </div>
  );
};

const ArrowDown = ({ label }) => (
  <div className="flex flex-col items-center justify-center h-12 relative z-0">
    {label && <span className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded-full absolute -ml-32">{label}</span>}
    <div className="w-0.5 bg-gray-300 h-full"></div>
    <div className="w-3 h-3 border-r-2 border-b-2 border-gray-300 transform rotate-45 -mt-2 bg-gray-50"></div>
  </div>
);

const PipelineCore = () => {
  return (
    <div className="flex flex-col items-center p-8 bg-gray-50 min-h-screen font-sans">
      <h1 className="text-3xl font-bold mb-2 text-gray-800">Golf Swing Pipeline Architecture</h1>
      <p className="text-gray-500 mb-8">Core pipeline: S3 upload through analysis</p>

      {/* Entry point */}
      <Node
        type="s3"
        title="S3: golf-swing-data"
        subtitle="path: {golfer}/raw/"
        details="Raw .MOV (iPhone HEVC 10-bit VFR) or .mp4 (Android)"
      />
      <ArrowDown label="S3 event (.MOV / .mp4)" />
      <Node
        type="sqs"
        title="SQS: golf-video-label"
      />
      <ArrowDown label="polls queue" />

      {/* GPU Worker */}
      <Node
        type="ec2"
        title="EC2 g6.2xlarge (Spot)"
        subtitle="8 vCPU, L4 24GB GPU"
        details="Auto-terminates on idle. Runs worker.py"
      >
        <div className="flex flex-col gap-2 mt-2">
          <div className="bg-white p-2 rounded text-xs text-left border border-purple-200">
            <strong className="text-purple-700">Step 1: Transcode</strong>
            <br />NVDEC decode (HEVC) → NVENC encode (H.264 CFR). ~24s for 5800 frames.
          </div>
          <div className="bg-white p-2 rounded text-xs text-left border border-purple-200">
            <strong className="text-purple-700">Step 2: Label (Turbo Mode)</strong>
            <br />NVDEC h264_cuvid → CPU prep → GPU infer.
            Batched RTMDet + ViTPose-Huge (torch.compile). ~57.5 fps steady-state.
          </div>
        </div>
      </Node>

      <div className="flex w-full max-w-xl justify-between mt-4">
         <div className="flex flex-col items-center">
           <ArrowDown label="uploads 1.2MB .pkl" />
           <Node type="s3" title="S3: /keypoints" />
         </div>
         <div className="flex flex-col items-center">
           <ArrowDown label="uploads .mp4" />
           <Node type="s3" title="S3: /processed" />
         </div>
      </div>

      {/* Swing Detection Lambda */}
      <div className="flex flex-col items-center mt-4">
        <ArrowDown label="S3 event (.pkl)" />
        <Node
          type="lambda"
          title="Lambda: swing_detect"
          details="~13s signal processing. Detects Backswings & Contacts."
        />

        <div className="flex w-full justify-between mt-4 gap-4">
          <div className="flex flex-col items-center w-1/2">
            <ArrowDown label="PutItem" />
            <Node type="db" title="DynamoDB" subtitle="golf-swing-detections" />
          </div>
          <div className="flex flex-col items-center w-1/2">
            <ArrowDown label="uploads .json" />
            <Node type="s3" title="S3: /detection" />
          </div>
        </div>
      </div>

      {/* Post Processing Lambda */}
      <div className="flex flex-col items-center mt-4">
        <ArrowDown label="S3 event (.json)" />
        <Node
          type="lambda"
          title="Lambda: post_processing"
          details="Reads .json, .pkl, .mp4. Generates visualizations & predictions."
        >
          <div className="mt-2 text-xs text-left bg-orange-50 p-2 rounded border border-orange-200">
            <ul className="list-disc pl-4 space-y-1">
              <li>S3 <strong>/fingers</strong> (JSON)</li>
              <li>S3 <strong>/frames</strong> (JPG overlays)</li>
              <li>S3 <strong>/output</strong> (Grids, plots)</li>
              <li>DynamoDB (update fingers)</li>
              <li>Pushover Notification</li>
            </ul>
          </div>
        </Node>
      </div>

      {/* Analyze (manual, separate flow) */}
      <div className="flex flex-col items-center mt-8 border-t-2 border-dashed border-gray-200 pt-8 w-full max-w-xl">
        <p className="text-xs font-bold uppercase text-gray-400 mb-4 tracking-wider">On-demand (manual invoke)</p>
        <Node
          type="lambda"
          title="Lambda: analyze"
          details={"Requires: golfer, score thresholds, phases.\nGenerates SPM plots + Gemini text analysis."}
        />
        <ArrowDown />
        <div className="flex gap-4">
          <Node type="s3" title="S3: /analysis" details="Plots, Gemini TXT" />
          <Node type="db" title="DynamoDB" subtitle="ANALYSIS item" />
          <Node type="default" title="Pushover" subtitle="Mobile Notification" />
        </div>
      </div>
    </div>
  );
};

export default PipelineCore;

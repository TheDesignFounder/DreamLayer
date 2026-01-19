import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Copy, ChevronDown, Calculator } from 'lucide-react';

interface EvalMetricsProps {
  imageId: string;
  imagePath: string;
  prompt?: string;
  metrics?: {
    clip_score_mean?: number;
    clip_score_median?: number;
    clip_score_std?: number;
    clip_score_max?: number;
    clip_score_min?: number;
    fid_score?: number;
    // Object Detection Metrics (YOLO)
    object_precision?: number;
    object_recall?: number;
    object_f1?: number;
    detected_objects?: Record<string, number>;
    missing_objects?: Record<string, number>;
    // Visual Composition Metrics
    composition_score?: number;
    rule_of_thirds_score?: number;
    symmetry_score?: number;
    balance_score?: number;
    // Aesthetic Quality Metrics (Phase 5)
    aesthetics_score?: number;  // LAION aesthetic score (1-10)
    color_harmony_score?: number;
    saturation_balance?: number;
    value_contrast?: number;
    technical_quality_score?: number;
    sharpness_score?: number;
    noise_level?: number;
    artifact_score?: number;
    overall_aesthetic_quality?: number;
    // Legacy/additional metrics
    composition_precision?: number;
    composition_recall?: number;
    composition_f1?: number;
    lpips_score?: number;
    psnr_score?: number;
    ssim_score?: number;
    nsfw_score?: number;
    computed_at?: string;
  };
  isLoading?: boolean;
  onCalculateMetrics?: () => Promise<void>;
}

const EvalMetrics: React.FC<EvalMetricsProps> = ({
  imageId,
  imagePath,
  prompt,
  metrics,
  isLoading = false,
  onCalculateMetrics
}) => {
  const [expanded, setExpanded] = useState(true);

  const getScoreColor = (score: number | undefined, metricType: 'clip' | 'fid' | 'composition' | 'aesthetics' | 'visual' | 'technical' | 'noise' | 'lpips' | 'ssim' | 'psnr') => {
    if (score === undefined) return 'text-muted-foreground';

    switch (metricType) {
      case 'clip':
        // CLIP score: 0.3+ good, 0.2-0.3 moderate, <0.2 poor
        if (score >= 0.3) return 'text-green-600';
        if (score >= 0.2) return 'text-yellow-600';
        return 'text-red-600';

      case 'fid':
        // FID: lower is better. <50 good, 50-100 moderate, >100 poor
        if (score < 50) return 'text-green-600';
        if (score < 100) return 'text-yellow-600';
        return 'text-red-600';

      case 'composition':
        // Object detection F1: 0.7+ good, 0.5-0.7 moderate, <0.5 poor
        if (score >= 0.7) return 'text-green-600';
        if (score >= 0.5) return 'text-yellow-600';
        return 'text-red-600';

      case 'visual':
        // Visual composition: 0.6+ good, 0.4-0.6 moderate, <0.4 poor
        if (score >= 0.6) return 'text-green-600';
        if (score >= 0.4) return 'text-yellow-600';
        return 'text-red-600';

      case 'aesthetics':
        // Aesthetics: 6+ good, 4-6 moderate, <4 poor (scale 1-10)
        if (score >= 6) return 'text-green-600';
        if (score >= 4) return 'text-yellow-600';
        return 'text-red-600';

      case 'technical':
        // Technical quality: 0.7+ good, 0.5-0.7 moderate, <0.5 poor
        if (score >= 0.7) return 'text-green-600';
        if (score >= 0.5) return 'text-yellow-600';
        return 'text-red-600';

      case 'noise':
        // Noise/artifacts: lower is better. <0.3 good, 0.3-0.5 moderate, >0.5 poor
        if (score < 0.3) return 'text-green-600';
        if (score < 0.5) return 'text-yellow-600';
        return 'text-red-600';

      case 'lpips':
        // LPIPS: lower is better (perceptual similarity). <0.3 good, 0.3-0.5 moderate, >0.5 poor
        if (score < 0.3) return 'text-green-600';
        if (score < 0.5) return 'text-yellow-600';
        return 'text-red-600';

      case 'ssim':
        // SSIM: higher is better. >0.9 good, 0.7-0.9 moderate, <0.7 poor
        if (score >= 0.9) return 'text-green-600';
        if (score >= 0.7) return 'text-yellow-600';
        return 'text-red-600';

      case 'psnr':
        // PSNR: higher is better. >30 good, 20-30 moderate, <20 poor
        if (score >= 30) return 'text-green-600';
        if (score >= 20) return 'text-yellow-600';
        return 'text-red-600';
    }
  };

  const handleCopyMetrics = () => {
    if (!metrics) return;

    const metricsText = JSON.stringify(metrics, null, 2);
    navigator.clipboard.writeText(metricsText);
  };

  const formatScore = (score: number | undefined, decimals: number = 4) => {
    if (score === undefined) return 'N/A';
    return score.toFixed(decimals);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium">Evaluation Metrics</span>
        <div className="flex items-center gap-2">
          {onCalculateMetrics && (
            <Button
              variant="outline"
              size="sm"
              className="text-xs h-8"
              onClick={onCalculateMetrics}
              disabled={isLoading}
            >
              <Calculator className="w-3 h-3 mr-1" />
              {isLoading ? 'Calculating...' : 'Calculate'}
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            className="text-xs h-8"
            onClick={handleCopyMetrics}
            disabled={!metrics}
          >
            <Copy className="w-3 h-3 mr-1" />
            Copy Metrics
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={() => setExpanded(!expanded)}
          >
            <ChevronDown className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} />
          </Button>
        </div>
      </div>

      {expanded && (
        <div className="bg-muted p-3 rounded-md text-xs leading-relaxed">
          {!metrics ? (
            <div className="text-muted-foreground">
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                  <span>Computing metrics...</span>
                </div>
              ) : (
                "No metrics computed yet. Click 'Calculate' to compute evaluation metrics."
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {/* CLIP Score */}
              {metrics.clip_score_mean !== undefined && (
                <div>
                  <div className="font-semibold mb-1">CLIP Score (Text-Image Alignment):</div>
                  <div className="space-y-1">
                    <div className={getScoreColor(metrics.clip_score_mean, 'clip')}>
                      <strong>Mean:</strong> {formatScore(metrics.clip_score_mean)}
                    </div>
                  </div>
                </div>
              )}

              {/* FID Score */}
              {metrics.fid_score !== undefined && (
                <div>
                  <div className="font-semibold mb-1">FID Score (Image Quality):</div>
                  <div className={getScoreColor(metrics.fid_score, 'fid')}>
                    {formatScore(metrics.fid_score, 2)} (lower is better)
                  </div>
                </div>
              )}

              {/* Object Detection Metrics (YOLO) */}
              {(metrics.object_precision !== undefined ||
                metrics.object_recall !== undefined ||
                metrics.object_f1 !== undefined) && (
                <div>
                  <div className="font-semibold mb-1">Object Detection (Prompt Accuracy):</div>
                  <div className="space-y-1">
                    {metrics.object_f1 !== undefined && (
                      <div className={getScoreColor(metrics.object_f1, 'composition')}>
                        <strong>F1 Score:</strong> {formatScore(metrics.object_f1)}
                      </div>
                    )}
                    {metrics.object_precision !== undefined && (
                      <div className="text-muted-foreground">
                        <strong>Precision:</strong> {formatScore(metrics.object_precision)}
                      </div>
                    )}
                    {metrics.object_recall !== undefined && (
                      <div className="text-muted-foreground">
                        <strong>Recall:</strong> {formatScore(metrics.object_recall)}
                      </div>
                    )}
                    {metrics.detected_objects && Object.keys(metrics.detected_objects).length > 0 && (
                      <div className="text-muted-foreground text-xs">
                        <strong>Detected:</strong> {Object.entries(metrics.detected_objects).map(([k, v]) => `${k}(${v})`).join(', ')}
                      </div>
                    )}
                    {metrics.missing_objects && Object.keys(metrics.missing_objects).length > 0 && (
                      <div className="text-red-500 text-xs">
                        <strong>Missing:</strong> {Object.entries(metrics.missing_objects).map(([k, v]) => `${k}(${v})`).join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Visual Composition Metrics */}
              {(metrics.composition_score !== undefined ||
                metrics.rule_of_thirds_score !== undefined ||
                metrics.symmetry_score !== undefined ||
                metrics.balance_score !== undefined) && (
                <div>
                  <div className="font-semibold mb-1">Visual Composition:</div>
                  <div className="space-y-1">
                    {metrics.composition_score !== undefined && (
                      <div className={getScoreColor(metrics.composition_score, 'visual')}>
                        <strong>Overall:</strong> {formatScore(metrics.composition_score)}
                      </div>
                    )}
                    {metrics.rule_of_thirds_score !== undefined && (
                      <div className="text-muted-foreground">
                        <strong>Rule of Thirds:</strong> {formatScore(metrics.rule_of_thirds_score)}
                      </div>
                    )}
                    {metrics.symmetry_score !== undefined && (
                      <div className="text-muted-foreground">
                        <strong>Symmetry:</strong> {formatScore(metrics.symmetry_score)}
                      </div>
                    )}
                    {metrics.balance_score !== undefined && (
                      <div className="text-muted-foreground">
                        <strong>Balance:</strong> {formatScore(metrics.balance_score)}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Aesthetic Quality Metrics */}
              {(metrics.aesthetics_score !== undefined ||
                metrics.color_harmony_score !== undefined ||
                metrics.technical_quality_score !== undefined ||
                metrics.overall_aesthetic_quality !== undefined) && (
                <div>
                  <div className="font-semibold mb-1">Aesthetic Quality:</div>
                  <div className="space-y-1">
                    {metrics.aesthetics_score !== undefined && (
                      <div className={getScoreColor(metrics.aesthetics_score, 'aesthetics')}>
                        <strong>LAION Aesthetic:</strong> {formatScore(metrics.aesthetics_score, 2)}/10
                      </div>
                    )}
                    {metrics.color_harmony_score !== undefined && (
                      <div className={getScoreColor(metrics.color_harmony_score, 'visual')}>
                        <strong>Color Harmony:</strong> {formatScore(metrics.color_harmony_score)}
                      </div>
                    )}
                    {metrics.saturation_balance !== undefined && (
                      <div className="text-muted-foreground pl-3">
                        <strong>Saturation Balance:</strong> {formatScore(metrics.saturation_balance)}
                      </div>
                    )}
                    {metrics.value_contrast !== undefined && (
                      <div className="text-muted-foreground pl-3">
                        <strong>Value Contrast:</strong> {formatScore(metrics.value_contrast)}
                      </div>
                    )}
                    {metrics.technical_quality_score !== undefined && (
                      <div className={getScoreColor(metrics.technical_quality_score, 'technical')}>
                        <strong>Technical Quality:</strong> {formatScore(metrics.technical_quality_score)}
                      </div>
                    )}
                    {metrics.sharpness_score !== undefined && (
                      <div className="text-muted-foreground pl-3">
                        <strong>Sharpness:</strong> {formatScore(metrics.sharpness_score)}
                      </div>
                    )}
                    {metrics.noise_level !== undefined && (
                      <div className={`pl-3 ${getScoreColor(metrics.noise_level, 'noise')}`}>
                        <strong>Noise Level:</strong> {formatScore(metrics.noise_level)} (lower is better)
                      </div>
                    )}
                    {metrics.artifact_score !== undefined && (
                      <div className={`pl-3 ${getScoreColor(metrics.artifact_score, 'noise')}`}>
                        <strong>Artifacts:</strong> {formatScore(metrics.artifact_score)} (lower is better)
                      </div>
                    )}
                    {metrics.overall_aesthetic_quality !== undefined && (
                      <div className={`${getScoreColor(metrics.overall_aesthetic_quality, 'visual')} font-medium pt-1 border-t border-border/50`}>
                        <strong>Overall Aesthetic:</strong> {formatScore(metrics.overall_aesthetic_quality)}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Reference Comparison Metrics (img2img only) */}
              {(metrics.lpips_score !== undefined ||
                metrics.psnr_score !== undefined ||
                metrics.ssim_score !== undefined) && (
                <div>
                  <div className="font-semibold mb-1">Reference Comparison (img2img):</div>
                  <div className="space-y-1">
                    {metrics.ssim_score !== undefined && (
                      <div className={getScoreColor(metrics.ssim_score, 'ssim')}>
                        <strong>SSIM:</strong> {formatScore(metrics.ssim_score)} (higher is better)
                      </div>
                    )}
                    {metrics.psnr_score !== undefined && (
                      <div className={getScoreColor(metrics.psnr_score, 'psnr')}>
                        <strong>PSNR:</strong> {formatScore(metrics.psnr_score, 2)} dB (higher is better)
                      </div>
                    )}
                    {metrics.lpips_score !== undefined && (
                      <div className={getScoreColor(metrics.lpips_score, 'lpips')}>
                        <strong>LPIPS:</strong> {formatScore(metrics.lpips_score)} (lower is better)
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* NSFW Score (if available) */}
              {metrics.nsfw_score !== undefined && (
                <div>
                  <div className="font-semibold mb-1">Safety:</div>
                  <div className="text-muted-foreground">
                    <strong>NSFW Score:</strong> {formatScore(metrics.nsfw_score)}
                  </div>
                </div>
              )}

              {/* Computed At */}
              {metrics.computed_at && (
                <div className="text-xs text-muted-foreground pt-2 border-t">
                  Computed at: {new Date(metrics.computed_at).toLocaleString()}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EvalMetrics;

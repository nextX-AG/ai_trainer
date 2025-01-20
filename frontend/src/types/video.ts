export interface VideoMetadata {
    fps: number;
    totalFrames: number;
    width: number;
    height: number;
    duration: number;
    codec: string;
}

export interface ProcessingStats {
    framesProcessed: number;
    facesDetected: number;
    avgFaceSize: [number, number];
    qualityScore: number;
    problemFrames: number[];
}

export interface VideoAnalysis {
    metadata: VideoMetadata;
    stats: ProcessingStats;
    recommendations: string[];
    status: string;
} 
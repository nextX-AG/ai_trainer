export interface FaceSwapConfig {
    framework: string;
    modelType: string;
    resolution: number;
    batchSize: number;
    iterations: number;
    targetFeatures: string[];
}

export interface FaceSwapStatus {
    projectId: string;
    stage: 'preparing' | 'extracting' | 'training' | 'converting';
    progress: number;
    currentIteration?: number;
    totalIterations?: number;
    error?: string;
}

export interface ConversionOptions {
    denoisePower: number;
    colorCorrection: boolean;
    faceAlignment: boolean;
} 
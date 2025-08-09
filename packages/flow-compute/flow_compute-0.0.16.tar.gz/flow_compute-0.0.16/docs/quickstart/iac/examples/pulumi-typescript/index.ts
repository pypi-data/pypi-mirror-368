// Basic Pulumi TypeScript example for Flow GPU tasks

import * as flow from "@pulumi/flow";
import * as pulumi from "@pulumi/pulumi";

// Get configuration
const config = new pulumi.Config();
const modelName = config.get("modelName") || "meta-llama/Llama-2-7b-chat-hf";
const instanceType = config.get("instanceType") || "l40s";
const useSpot = config.getBoolean("useSpot") ?? true;

// Create vLLM inference server
const inferenceServer = new flow.Task("vllm-server", {
    name: "vllm-inference-pulumi",
    command: `
        pip install vllm
        vllm serve ${modelName} \
            --host 0.0.0.0 \
            --port 8000 \
            --max-model-len 4096
    `,
    instanceType: instanceType,
    
    // Resource limits
    maxRunTimeHours: 24,
    maxPricePerHour: 1.50,
    
    // Spot instances
    spotInstance: useSpot,
    maxInterruptions: 3,
    
    // Networking
    ports: [8000],
    
    // Tags
    tags: {
        purpose: "quickstart",
        type: "inference",
        stack: pulumi.getStack(),
    },
});

// Export useful information
export const taskId = inferenceServer.id;
export const endpoint = inferenceServer.endpoints.apply(e => e["8000"]);
export const estimatedHourlyCost = inferenceServer.estimatedCostPerHour;
export const status = inferenceServer.status;

// Show cost savings with spot
export const costSavings = pulumi.all([
    inferenceServer.estimatedCostPerHour,
    useSpot
]).apply(([cost, spot]) => {
    if (spot) {
        const onDemandCost = 1.20; // l40s on-demand price
        const savings = ((onDemandCost - cost) / onDemandCost * 100).toFixed(0);
        return `${savings}% savings with spot instances`;
    }
    return "Using on-demand pricing";
});
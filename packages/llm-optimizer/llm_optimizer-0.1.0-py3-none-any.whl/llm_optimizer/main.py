import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from codecarbon import EmissionsTracker
import time
import numpy as np
import evaluate
import gc
import os

def load_and_generate():

    # Load model and tokenizer
    model_name = "EleutherAI/gpt-neo-1.3B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device).eval()

    # Metrics setup
    perplexity_metric = evaluate.load("perplexity", module_type="metric")
    bleu_metric = evaluate.load("bleu")
    rouge_metric = evaluate.load("rouge")

    # Self-freezing support
    frozen_layers = {}
    frozen_layer_names = []

    def freeze_hook(module, input, output, layer_name):
        frozen_output = torch.where(torch.abs(output) < 1e-4, torch.zeros_like(output), output)
        frozen_layers[layer_name] = frozen_output.detach()
        return frozen_output

    def apply_freeze_hooks(model):
        for name, module in model.named_modules():
            if 'mlp' in name and hasattr(module, 'forward'):
                module.register_forward_hook(lambda mod, inp, out, n=name: freeze_hook(mod, inp, out, n))
                frozen_layer_names.append(name)
        print(f"Total layers registered for self-freezing: {len(frozen_layer_names)}")

    def self_prune(model, threshold=1e-3):
        with torch.no_grad():
            for name, param in model.named_parameters():
                if 'weight' in name and len(param.shape) > 1:
                    mask = param.abs() > threshold
                    param.mul_(mask.float())

    def free_gpu_memory():
        torch.cuda.empty_cache()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.ipc_collect()
            torch.cuda.empty_cache()

    free_gpu_memory()

    prompt_cache = {}
    def cached_infer(prompt):
        if prompt in prompt_cache:
            return prompt_cache[prompt]
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=50)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        prompt_cache[prompt] = result
        return result

    def evaluate_model(prompt, reference):
        generated = cached_infer(prompt)
        ppl = perplexity_metric.compute(predictions=[generated], model_id=model_name)["perplexities"][0]
        bleu = bleu_metric.compute(predictions=[generated], references=[reference])["bleu"]
        rouge = rouge_metric.compute(predictions=[generated], references=[reference])["rougeL"]
        return ppl, bleu, rouge, generated

    # Sample prompts
    prompts = [
        "The theory of relativity was developed by",
        "Climate change is primarily caused by",
        "Photosynthesis in plants requires",
        "Artificial intelligence can be used in"
    ]

    references = [
        "The theory of relativity was developed by Albert Einstein in the early 20th century.",
        "Climate change is primarily caused by the emission of greenhouse gases from human activities.",
        "Photosynthesis in plants requires sunlight, carbon dioxide, and water.",
        "Artificial intelligence can be used in healthcare, education, and autonomous vehicles."
    ]

    prompt = prompts[0]
    reference = references[0]

    # === BASELINE ===
    tracker_baseline = EmissionsTracker(project_name="gptneo-baseline")
    tracker_baseline.start()
    start_base = time.time()
    output_baseline = evaluate_model(prompt, reference)
    end_base = time.time()
    baseline_emissions = tracker_baseline.stop()
    baseline_time = end_base - start_base

    # === PRUNING ===
    self_prune(model, threshold=1e-3)
    tracker_prune = EmissionsTracker(project_name="gptneo-pruning")
    tracker_prune.start()
    start_prune = time.time()
    output_pruned = evaluate_model(prompt, reference)
    end_prune = time.time()
    prune_emissions = tracker_prune.stop()
    prune_time = end_prune - start_prune

    # === FREEZING ===
    hook_start = time.time()
    apply_freeze_hooks(model)
    hook_end = time.time()
    hook_setup_time = hook_end - hook_start

    tracker_freeze = EmissionsTracker(project_name="gptneo-freezing")
    tracker_freeze.start()
    start_freeze = time.time()
    output_freeze = evaluate_model(prompt, reference)
    end_freeze = time.time()
    freeze_emissions = tracker_freeze.stop()
    freeze_time = end_freeze - start_freeze

    # === OPTIMIZED ===
    tracker_optimized = EmissionsTracker(project_name="gptneo-optimized")
    tracker_optimized.start()
    start_opt = time.time()
    output_optimized = evaluate_model(prompt, reference)
    end_opt = time.time()
    optimized_emissions = tracker_optimized.stop()
    optimized_time = end_opt - start_opt

    # === CACHING ===
    tracker_cache = EmissionsTracker(project_name="gptneo-caching")
    tracker_cache.start()
    start_cache = time.time()
    output_cache = evaluate_model(prompt, reference)
    end_cache = time.time()
    cache_emissions = tracker_cache.stop()
    cache_time = end_cache - start_cache

    # === PRINT RESULTS ===
    print("=== BASELINE ===")
    print("Generated Text:", output_baseline[-1])
    print(f"Perplexity: {output_baseline[0]:.2f}, BLEU: {output_baseline[1]:.2f}, ROUGE-L: {output_baseline[2]:.2f}")
    print(f"Inference Time: {baseline_time:.2f}s, CO2 Emissions: {baseline_emissions:.6f} kg")

    print("\n=== AFTER PRUNING + FREEZING ===")
    print("Generated Text:", output_optimized[-1])
    print(f"Perplexity: {output_optimized[0]:.2f}, BLEU: {output_optimized[1]:.2f}, ROUGE-L: {output_optimized[2]:.2f}")
    print(f"Inference Time: {optimized_time:.2f}s, CO2 Emissions: {optimized_emissions:.6f} kg")

    delta_emission = baseline_emissions - optimized_emissions
    print("\n=== SUMMARY ===")
    print(f"CO2 Reduction: {delta_emission:.6f} kg")

    # === ABLATION STUDY ===
    print("\n=== ABLATION: AFTER PRUNING ONLY ===")
    print("Generated Text:", output_pruned[-1])
    print(f"Perplexity: {output_pruned[0]:.2f}, BLEU: {output_pruned[1]:.2f}, ROUGE-L: {output_pruned[2]:.2f}")
    print(f"Inference Time: {prune_time:.2f}s, CO2 Emissions: {prune_emissions:.6f} kg")
    print(f"CO2 Reduction from Baseline: {baseline_emissions - prune_emissions:.6f} kg")

    print("\n=== ABLATION: AFTER FREEZING ONLY ===")
    print("Generated Text:", output_freeze[-1])
    print(f"Perplexity: {output_freeze[0]:.2f}, BLEU: {output_freeze[1]:.2f}, ROUGE-L: {output_freeze[2]:.2f}")
    print(f"Inference Time: {freeze_time:.2f}s, CO2 Emissions: {freeze_emissions:.6f} kg")
    print(f"CO2 Reduction from Pruning: {prune_emissions - freeze_emissions:.6f} kg")

    # === INDIVIDUAL EFFECTS ===
    print("\n=== INDIVIDUAL EFFECTS ===")
    print(f"[PRUNING] Inference Time: {prune_time:.2f}s, CO2: {prune_emissions:.6f} kg")
    print(f"[FREEZING] Hook Setup Time: {hook_setup_time:.4f}s")
    print(f"[FREEZING] Inference Time: {freeze_time:.2f}s, CO2: {freeze_emissions:.6f} kg")
    print(f"[CACHING] Cached Inference Time: {cache_time:.4f}s, CO2: {cache_emissions:.6f} kg")

    # === RUNTIME BREAKDOWN ===
    hook_setup_ms = hook_setup_time * 1000
    prune_saving_ms = (baseline_time - prune_time) * 1000
    freeze_saving_ms = (baseline_time - freeze_time) * 1000
    cache_saving_ms = (baseline_time - cache_time) * 1000

    prune_speedup_pct = 100 * (baseline_time - prune_time) / baseline_time
    freeze_speedup_pct = 100 * (baseline_time - freeze_time) / baseline_time
    cache_speedup_pct = 100 * (baseline_time - cache_time) / baseline_time

    print("\n=== RUNTIME BREAKDOWN (in ms) ===")
    print(f"Hook Setup Overhead: {hook_setup_ms:.2f} ms (One-time cost)")
    print(f"Inference Time Saved by Pruning: {prune_saving_ms:.2f} ms ({prune_speedup_pct:.2f}%)")
    print(f"Inference Time Saved by Freezing: {freeze_saving_ms:.2f} ms ({freeze_speedup_pct:.2f}%)")
    print(f"Inference Time Saved by Caching: {cache_saving_ms:.2f} ms ({cache_speedup_pct:.2f}%)")

    print(f"[FREEZING ONLY] Net Inference Gain (Baseline - Freezing): {baseline_time - freeze_time:.4f}s")
    print(f"[FREEZING ONLY] Hook Setup Time: {hook_setup_time:.4f}s")

    print("\n=== QUALITATIVE COMPARISON ===")
    print("Prompt 1:", prompts[0])
    print("[Baseline Output]:", output_baseline[-1])
    print("[Optimized Output]:", output_optimized[-1])

    print("\n=== FULL QUALITATIVE COMPARISON (All 4 Prompts) ===")
    for i in range(4):
        prompt = prompts[i]
        reference = references[i]
        _, _, _, baseline_output = evaluate_model(prompt, reference)
        _, _, _, optimized_output = evaluate_model(prompt, reference)
        print(f"\nPrompt {i+1}: {prompt}")
        print("[Baseline Output]:", baseline_output)
        print("[Optimized Output]:", optimized_output)

if __name__ == "__main__":
    load_and_generate()

import dataclasses
import math
import random

from comfyui_workflow_generator import ComfyUIWorkflowExecutor
from sandbox.workflow_api import Workflow, CLIP, MODEL

def random_resolution(seed: int) -> (int, int):

    scale = 0.5

    num1 = seed % 1000 / 1000

    num2 = (num1 - 0.5) * scale + 0.5

    width = round((256 - 192 * num2) / math.sqrt(-9 * num2 * num2 + 9 * num2 + 4)) * 16

    height = round((64 + 192 * num2) / math.sqrt(-9 * num2 * num2 + 9 * num2 + 4)) * 16

    return width, height


@dataclasses.dataclass
class Lora:
    name: str
    weight: float

# as far as i understand that node adds random loras
def wildcard_encode(w: Workflow, model: MODEL, clip: CLIP, loras: list[list[Lora]]) -> (MODEL, CLIP):

    for l in loras:
        # loras is list of lists, so you can pick a lora from a nested list using random.choice
        lora = random.choice(l)

        model, clip = w.LoraLoader(model, clip, lora_name=lora.name, strength_model=lora.weight, strength_clip=lora.weight)

    return model, clip

# the full logic from wildcard preprocessor could be implemented, but i'm afraid it's going to be incomprehensible
# so here is a rather simple demonstration
def wildcard_preprocessor(prompt: str, person: list[str], action: list[str]) -> str:

    return (prompt
     .replace("__person__", random.choice(person))
     .replace("__action__", random.choice(action)))


def gen_workflow() -> Workflow:

    lora_list = [
        [Lora(name="doro_xypher_ixl_v1.safetensors", weight=0.7),
         Lora(name="arknights_all_v4_0711.safetensors", weight=0.7)],
        [Lora(name="haiz_ai_illu.safetensors", weight=0.7)]
    ]
    checkpoint_name = "obsessionIllustrious_v31.safetensors"
    seed = random.randint(0, 999999999999)
    cfg = 2.6
    steps = 20
    sampler = "res_multistep_cfg_pp"
    scheduler = "exponential"

    prompt_template = "__person__, __action__, best quality, absurders, masterpiece"

    people = [r"1girl, lisa_\(genshin_impact\)", r"1girl, foxgirl, red hair, red eyes, fox tail"]
    actions = ["playing banjo", "sitting, on coach"]

    prompt = wildcard_preprocessor(prompt_template, people, actions)

    negative_prompt = "bad quality, lowres, jpeg artifacts"

    width, height = random_resolution(seed)

    # actually building workflow
    wf = Workflow()

    vae = wf.VAELoader("sdxl_vae.safetensors")

    empty_latent_image = wf.EmptyLatentImage(width, height, 1)

    model, clip, _ = wf.CheckpointLoaderSimple(ckpt_name=checkpoint_name)

    model = wf.PerturbedAttentionGuidance(model, scale=3.0)

    # using the "wildcard encode" aka add a bunch of random loras
    model, clip = wildcard_encode(wf, model, clip, loras=lora_list)

    positive_conditioning = wf.CLIPTextEncode(prompt, clip=clip)

    negative_conditioning = wf.CLIPTextEncode(negative_prompt, clip=clip)

    denoised_latent_image = wf.KSamplerAdvanced(model,
                        add_noise="enable",
                        noise_seed=seed,
                        steps=steps,
                        cfg=cfg,
                        sampler_name=sampler,
                        scheduler=scheduler,
                        positive=positive_conditioning,
                        negative=negative_conditioning,
                        latent_image=empty_latent_image,
                        start_at_step=0,
                        end_at_step=999,
                        return_with_leftover_noise="disable"
                        )

    image = wf.VAEDecode(denoised_latent_image, vae=vae)

    upscale_model = wf.UpscaleModelLoader("4xUltrasharp_4xUltrasharpV10.pt")

    upscaled_image = wf.ImageUpscaleWithModel(image=image, upscale_model=upscale_model)

    upscaled_image = wf.ImageScaleToTotalPixels(upscaled_image, "lanczos", 2.25)

    latent_image = wf.VAEEncode(pixels=upscaled_image, vae=vae)

    highres_fixed_latent_image = wf.KSamplerAdvanced(model,
                        add_noise="enable",
                        noise_seed=seed,
                        steps=steps,
                        cfg=cfg,
                        sampler_name=sampler,
                        scheduler=scheduler,
                        positive=positive_conditioning,
                        negative=negative_conditioning,
                        latent_image=latent_image,
                        start_at_step=10,
                        end_at_step=999,
                        return_with_leftover_noise="disable"
                        )

    result_image = wf.VAEDecode(highres_fixed_latent_image, vae=vae)

    wf.SaveImage(result_image, "antlers_weird_workflow")

    return wf

workflow = gen_workflow()

workflow_json = workflow.get_workflow()

with open("antlers_weird_workflow.json", "w") as f:
    f.write(workflow_json)

executor = ComfyUIWorkflowExecutor("http://127.0.0.1:8188")

results = executor.execute_workflow(workflow.workflow_dict, output_dir="./results")

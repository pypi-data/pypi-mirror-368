# Import the generated API
from dataclasses import dataclass

from workflow_api import Workflow, CLIP, MODEL
from comfyui_workflow_generator import ComfyUIWorkflowExecutor

# Step 1: Upload image with custom name
executor = ComfyUIWorkflowExecutor("http://127.0.0.1:8188")
uploaded_filename = executor.upload_image(
    "my_very_own_image.png", 
    image_name="my_very_own_image.png"
)

@dataclass
class LoraName:
    name: str
    weight: float

lora_list = [
    LoraName(name="748cm-NoobEPS100-lokr-v03-000080.safetensors", weight=0.5),
    LoraName(name="grace_heiden_IL10_01_resized.safetensors", weight=0.5),
    LoraName(name="cookie-run-style.safetensors", weight=0.5),
]

def load_lora_stack(wf: Workflow, model: MODEL, clip: CLIP, loras: list[LoraName]) -> (MODEL, CLIP):

    for lora in loras:

        model, clip = wf.LoraLoader(model, clip, lora_name=lora.name, strength_model=lora.weight, strength_clip=lora.weight)

    return model, clip



def gen_workflow() -> Workflow:
    # Step 2: Create workflow
    wf = Workflow()

    # Load checkpoint
    model, clip, _ = wf.CheckpointLoaderSimple(ckpt_name="Illustrious-XL-v1.0.safetensors")

    model, clip = load_lora_stack(wf, model, clip, lora_list)

    # Load vae, i usually do it via separate node
    vae = wf.VAELoader(vae_name="sdxl_vae.safetensors")

    # Load uploaded image (use the uploaded filename)
    image, mask = wf.LoadImage(image="my_very_own_image.png")

    # Encode prompts
    positive = wf.CLIPTextEncode(text="1girl, lisa_\(genshin_impact\)", clip=clip)
    negative = wf.CLIPTextEncode(text="blurry, low quality", clip=clip)

    # Encode image for img2img
    latent = wf.VAEEncode(pixels=image, vae=vae)

    # Sample
    denoized_latent = wf.KSampler(
        model=model,
        seed=42,
        steps=20,
        cfg=8.0,
        sampler_name="euler",
        scheduler="normal",
        positive=positive,
        negative=negative,
        latent_image=latent,
        denoise=0.8
    )

    # Decode
    result_image = wf.VAEDecode(samples=denoized_latent, vae=vae)

    # Save
    wf.SaveImage(images=result_image, filename_prefix="lisa_from_genshin")

    return wf

workflow = gen_workflow()

# Step 3: Get workflow JSON (for debugging or manual inspection)
workflow_json = workflow.get_workflow()
print("Generated workflow:", workflow_json)

with open("workflow_json.json", "w") as f:
    f.write(workflow_json)

# # Step 4: Execute it (do not feed it with json, it expects dict)
# results = executor.execute_workflow(workflow.workflow_dict, output_dir="./results")


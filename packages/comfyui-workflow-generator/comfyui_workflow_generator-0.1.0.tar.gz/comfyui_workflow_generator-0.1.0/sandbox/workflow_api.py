from uuid import uuid4
from typing import Any
from json import dumps


def to_comfy_input(value: Any) ->Any:
    if isinstance(value, NodeOutput):
        return value.to_input()
    else:
        return value


def random_node_id() ->str:
    return str(uuid4())


class NodeOutput:

    def __init__(self, node_id, output_index):
        self.node_id = node_id
        self.output_index = output_index

    def to_input(self):
        return [self.node_id, self.output_index]


class StrNodeOutput(NodeOutput):
    pass


class FloatNodeOutput(NodeOutput):
    pass


class IntNodeOutput(NodeOutput):
    pass


class BoolNodeOutput(NodeOutput):
    pass


class AnyNodeOutput(NodeOutput):
    pass


class AUDIO(NodeOutput):
    pass


class AnyNodeOutput(NodeOutput):
    pass


class BASIC_PIPE(NodeOutput):
    pass


class BBOX_DETECTOR(NodeOutput):
    pass


class CAMERA_CONTROL(NodeOutput):
    pass


class CLIP(NodeOutput):
    pass


class CLIP_VISION(NodeOutput):
    pass


class CLIP_VISION_OUTPUT(NodeOutput):
    pass


class COMBO(NodeOutput):
    pass


class CONDITIONING(NodeOutput):
    pass


class CONTROL_NET(NodeOutput):
    pass


class DAMODEL(NodeOutput):
    pass


class DETAILER_HOOK(NodeOutput):
    pass


class DETAILER_PIPE(NodeOutput):
    pass


class FLOATS(NodeOutput):
    pass


class GEMINI_INPUT_FILES(NodeOutput):
    pass


class GLIGEN(NodeOutput):
    pass


class GUIDER(NodeOutput):
    pass


class HOOKS(NodeOutput):
    pass


class HOOK_KEYFRAMES(NodeOutput):
    pass


class IMAGE(NodeOutput):
    pass


class IPADAPTER_PIPE(NodeOutput):
    pass


class KSAMPLER(NodeOutput):
    pass


class KSAMPLER_ADVANCED(NodeOutput):
    pass


class LATENT(NodeOutput):
    pass


class LATENT_OPERATION(NodeOutput):
    pass


class LOAD3D_CAMERA(NodeOutput):
    pass


class LOAD_3D(NodeOutput):
    pass


class LOAD_3D_ANIMATION(NodeOutput):
    pass


class LORA_MODEL(NodeOutput):
    pass


class LOSS_MAP(NodeOutput):
    pass


class LUMA_CONCEPTS(NodeOutput):
    pass


class LUMA_REF(NodeOutput):
    pass


class MASK(NodeOutput):
    pass


class MESH(NodeOutput):
    pass


class MODEL(NodeOutput):
    pass


class MODEL_TASK_ID(NodeOutput):
    pass


class MODEL_TASK_ID_RIG_TASK_ID_RETARGET_TASK_ID(NodeOutput):
    pass


class NOISE(NodeOutput):
    pass


class OPENAI_CHAT_CONFIG(NodeOutput):
    pass


class OPENAI_INPUT_FILES(NodeOutput):
    pass


class OPTICAL_FLOW(NodeOutput):
    pass


class PHOTOMAKER(NodeOutput):
    pass


class PIXVERSE_TEMPLATE(NodeOutput):
    pass


class PK_HOOK(NodeOutput):
    pass


class POSE_KEYPOINT(NodeOutput):
    pass


class RECRAFT_COLOR(NodeOutput):
    pass


class RECRAFT_CONTROLS(NodeOutput):
    pass


class RECRAFT_V3_STYLE(NodeOutput):
    pass


class REGIONAL_PROMPTS(NodeOutput):
    pass


class RETARGET_TASK_ID(NodeOutput):
    pass


class RIG_TASK_ID(NodeOutput):
    pass


class SAMPLER(NodeOutput):
    pass


class SAM_MODEL(NodeOutput):
    pass


class SCHEDULER_FUNC(NodeOutput):
    pass


class SEGM_DETECTOR(NodeOutput):
    pass


class SEGS(NodeOutput):
    pass


class SEGS_HEADER(NodeOutput):
    pass


class SEGS_PREPROCESSOR(NodeOutput):
    pass


class SEG_ELT(NodeOutput):
    pass


class SEG_ELT_bbox(NodeOutput):
    pass


class SEG_ELT_control_net_wrapper(NodeOutput):
    pass


class SEG_ELT_crop_region(NodeOutput):
    pass


class SIGMAS(NodeOutput):
    pass


class STYLE_MODEL(NodeOutput):
    pass


class SVG(NodeOutput):
    pass


class TIMESTEPS_RANGE(NodeOutput):
    pass


class TRACKING(NodeOutput):
    pass


class TRANSFORMERS_CLASSIFIER(NodeOutput):
    pass


class UPSCALER(NodeOutput):
    pass


class UPSCALER_HOOK(NodeOutput):
    pass


class UPSCALE_MODEL(NodeOutput):
    pass


class VAE(NodeOutput):
    pass


class VIDEO(NodeOutput):
    pass


class VOXEL(NodeOutput):
    pass


class WAN_CAMERA_EMBEDDING(NodeOutput):
    pass


class WEBCAM(NodeOutput):
    pass


class Workflow:

    def __init__(self):
        self.workflow_dict = {}

    def _add_node(self, node_id, node):
        self.workflow_dict[node_id] = node

    def get_workflow(self) ->str:
        return dumps(self.workflow_dict, indent=2)

    def KSampler(self, model: MODEL, seed: int, steps: int, cfg: float,
        sampler_name: str, scheduler: str, positive: CONDITIONING, negative:
        CONDITIONING, latent_image: LATENT, denoise: float) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'seed': to_comfy_input(seed), 'steps': to_comfy_input(steps),
            'cfg': to_comfy_input(cfg), 'sampler_name': to_comfy_input(
            sampler_name), 'scheduler': to_comfy_input(scheduler),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'latent_image': to_comfy_input(
            latent_image), 'denoise': to_comfy_input(denoise)},
            'class_type': 'KSampler'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def CheckpointLoaderSimple(self, ckpt_name: str) ->(MODEL, CLIP, VAE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'ckpt_name': to_comfy_input(ckpt_name
            )}, 'class_type': 'CheckpointLoaderSimple'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP(node_id, 1), VAE(node_id, 2)

    def CLIPTextEncode(self, text: str, clip: CLIP) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'text': to_comfy_input(text), 'clip':
            to_comfy_input(clip)}, 'class_type': 'CLIPTextEncode'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def CLIPSetLastLayer(self, clip: CLIP, stop_at_clip_layer: int) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'stop_at_clip_layer': to_comfy_input(stop_at_clip_layer)},
            'class_type': 'CLIPSetLastLayer'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def VAEDecode(self, samples: LATENT, vae: VAE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'vae': to_comfy_input(vae)}, 'class_type': 'VAEDecode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def VAEEncode(self, pixels: IMAGE, vae: VAE) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'pixels': to_comfy_input(pixels),
            'vae': to_comfy_input(vae)}, 'class_type': 'VAEEncode'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def VAEEncodeForInpaint(self, pixels: IMAGE, vae: VAE, mask: MASK,
        grow_mask_by: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'pixels': to_comfy_input(pixels),
            'vae': to_comfy_input(vae), 'mask': to_comfy_input(mask),
            'grow_mask_by': to_comfy_input(grow_mask_by)}, 'class_type':
            'VAEEncodeForInpaint'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def VAELoader(self, vae_name: str) ->VAE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'vae_name': to_comfy_input(vae_name)},
            'class_type': 'VAELoader'}
        self._add_node(node_id, comfy_json_node)
        return VAE(node_id, 0)

    def EmptyLatentImage(self, width: int, height: int, batch_size: int
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'batch_size': to_comfy_input(
            batch_size)}, 'class_type': 'EmptyLatentImage'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentUpscale(self, samples: LATENT, upscale_method: str, width:
        int, height: int, crop: str) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'upscale_method': to_comfy_input(upscale_method), 'width':
            to_comfy_input(width), 'height': to_comfy_input(height), 'crop':
            to_comfy_input(crop)}, 'class_type': 'LatentUpscale'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentUpscaleBy(self, samples: LATENT, upscale_method: str,
        scale_by: float) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'upscale_method': to_comfy_input(upscale_method), 'scale_by':
            to_comfy_input(scale_by)}, 'class_type': 'LatentUpscaleBy'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentFromBatch(self, samples: LATENT, batch_index: int, length: int
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'batch_index': to_comfy_input(batch_index), 'length':
            to_comfy_input(length)}, 'class_type': 'LatentFromBatch'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def RepeatLatentBatch(self, samples: LATENT, amount: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'amount': to_comfy_input(amount)}, 'class_type':
            'RepeatLatentBatch'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def SaveImage(self, images: IMAGE, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'SaveImage'}
        self._add_node(node_id, comfy_json_node)

    def PreviewImage(self, images: IMAGE) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images)},
            'class_type': 'PreviewImage'}
        self._add_node(node_id, comfy_json_node)

    def LoadImage(self, image: str) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'LoadImage'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def LoadImageMask(self, image: str, channel: str) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'channel': to_comfy_input(channel)}, 'class_type': 'LoadImageMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def LoadImageOutput(self, image: COMBO) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'LoadImageOutput'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def ImageScale(self, image: IMAGE, upscale_method: str, width: int,
        height: int, crop: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'upscale_method': to_comfy_input(upscale_method), 'width':
            to_comfy_input(width), 'height': to_comfy_input(height), 'crop':
            to_comfy_input(crop)}, 'class_type': 'ImageScale'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageScaleBy(self, image: IMAGE, upscale_method: str, scale_by: float
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'upscale_method': to_comfy_input(upscale_method), 'scale_by':
            to_comfy_input(scale_by)}, 'class_type': 'ImageScaleBy'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageInvert(self, image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'ImageInvert'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageBatch(self, image1: IMAGE, image2: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image1': to_comfy_input(image1),
            'image2': to_comfy_input(image2)}, 'class_type': 'ImageBatch'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImagePadForOutpaint(self, image: IMAGE, left: int, top: int, right:
        int, bottom: int, feathering: int) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'left': to_comfy_input(left), 'top': to_comfy_input(top),
            'right': to_comfy_input(right), 'bottom': to_comfy_input(bottom
            ), 'feathering': to_comfy_input(feathering)}, 'class_type':
            'ImagePadForOutpaint'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def EmptyImage(self, width: int, height: int, batch_size: int, color: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'batch_size': to_comfy_input(
            batch_size), 'color': to_comfy_input(color)}, 'class_type':
            'EmptyImage'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ConditioningAverage(self, conditioning_to: CONDITIONING,
        conditioning_from: CONDITIONING, conditioning_to_strength: float
        ) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning_to': to_comfy_input(
            conditioning_to), 'conditioning_from': to_comfy_input(
            conditioning_from), 'conditioning_to_strength': to_comfy_input(
            conditioning_to_strength)}, 'class_type': 'ConditioningAverage'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ConditioningCombine(self, conditioning_1: CONDITIONING,
        conditioning_2: CONDITIONING) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning_1': to_comfy_input(
            conditioning_1), 'conditioning_2': to_comfy_input(
            conditioning_2)}, 'class_type': 'ConditioningCombine'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ConditioningConcat(self, conditioning_to: CONDITIONING,
        conditioning_from: CONDITIONING) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning_to': to_comfy_input(
            conditioning_to), 'conditioning_from': to_comfy_input(
            conditioning_from)}, 'class_type': 'ConditioningConcat'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ConditioningSetArea(self, conditioning: CONDITIONING, width: int,
        height: int, x: int, y: int, strength: float) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height), 'x': to_comfy_input(x), 'y':
            to_comfy_input(y), 'strength': to_comfy_input(strength)},
            'class_type': 'ConditioningSetArea'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ConditioningSetAreaPercentage(self, conditioning: CONDITIONING,
        width: float, height: float, x: float, y: float, strength: float
        ) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height), 'x': to_comfy_input(x), 'y':
            to_comfy_input(y), 'strength': to_comfy_input(strength)},
            'class_type': 'ConditioningSetAreaPercentage'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ConditioningSetAreaStrength(self, conditioning: CONDITIONING,
        strength: float) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'strength': to_comfy_input(strength)},
            'class_type': 'ConditioningSetAreaStrength'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ConditioningSetMask(self, conditioning: CONDITIONING, mask: MASK,
        strength: float, set_cond_area: str) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'mask': to_comfy_input(mask), 'strength':
            to_comfy_input(strength), 'set_cond_area': to_comfy_input(
            set_cond_area)}, 'class_type': 'ConditioningSetMask'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def KSamplerAdvanced(self, model: MODEL, add_noise: str, noise_seed:
        int, steps: int, cfg: float, sampler_name: str, scheduler: str,
        positive: CONDITIONING, negative: CONDITIONING, latent_image:
        LATENT, start_at_step: int, end_at_step: int,
        return_with_leftover_noise: str) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'add_noise': to_comfy_input(add_noise), 'noise_seed':
            to_comfy_input(noise_seed), 'steps': to_comfy_input(steps),
            'cfg': to_comfy_input(cfg), 'sampler_name': to_comfy_input(
            sampler_name), 'scheduler': to_comfy_input(scheduler),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'latent_image': to_comfy_input(
            latent_image), 'start_at_step': to_comfy_input(start_at_step),
            'end_at_step': to_comfy_input(end_at_step),
            'return_with_leftover_noise': to_comfy_input(
            return_with_leftover_noise)}, 'class_type': 'KSamplerAdvanced'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def SetLatentNoiseMask(self, samples: LATENT, mask: MASK) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'mask': to_comfy_input(mask)}, 'class_type': 'SetLatentNoiseMask'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentComposite(self, samples_to: LATENT, samples_from: LATENT, x:
        int, y: int, feather: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples_to': to_comfy_input(
            samples_to), 'samples_from': to_comfy_input(samples_from), 'x':
            to_comfy_input(x), 'y': to_comfy_input(y), 'feather':
            to_comfy_input(feather)}, 'class_type': 'LatentComposite'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentBlend(self, samples1: LATENT, samples2: LATENT, blend_factor:
        float) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples1': to_comfy_input(samples1),
            'samples2': to_comfy_input(samples2), 'blend_factor':
            to_comfy_input(blend_factor)}, 'class_type': 'LatentBlend'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentRotate(self, samples: LATENT, rotation: str) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'rotation': to_comfy_input(rotation)}, 'class_type': 'LatentRotate'
            }
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentFlip(self, samples: LATENT, flip_method: str) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'flip_method': to_comfy_input(flip_method)}, 'class_type':
            'LatentFlip'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentCrop(self, samples: LATENT, width: int, height: int, x: int,
        y: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'width': to_comfy_input(width), 'height': to_comfy_input(height
            ), 'x': to_comfy_input(x), 'y': to_comfy_input(y)},
            'class_type': 'LatentCrop'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LoraLoader(self, model: MODEL, clip: CLIP, lora_name: str,
        strength_model: float, strength_clip: float) ->(MODEL, CLIP):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'lora_name': to_comfy_input(
            lora_name), 'strength_model': to_comfy_input(strength_model),
            'strength_clip': to_comfy_input(strength_clip)}, 'class_type':
            'LoraLoader'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP(node_id, 1)

    def CLIPLoader(self, clip_name: str, type: str, device: str) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_name': to_comfy_input(clip_name
            ), 'type': to_comfy_input(type), 'device': to_comfy_input(
            device)}, 'class_type': 'CLIPLoader'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def UNETLoader(self, unet_name: str, weight_dtype: str) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'unet_name': to_comfy_input(unet_name
            ), 'weight_dtype': to_comfy_input(weight_dtype)}, 'class_type':
            'UNETLoader'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def DualCLIPLoader(self, clip_name1: str, clip_name2: str, type: str,
        device: str) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_name1': to_comfy_input(
            clip_name1), 'clip_name2': to_comfy_input(clip_name2), 'type':
            to_comfy_input(type), 'device': to_comfy_input(device)},
            'class_type': 'DualCLIPLoader'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def CLIPVisionEncode(self, clip_vision: CLIP_VISION, image: IMAGE, crop:
        str) ->CLIP_VISION_OUTPUT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_vision': to_comfy_input(
            clip_vision), 'image': to_comfy_input(image), 'crop':
            to_comfy_input(crop)}, 'class_type': 'CLIPVisionEncode'}
        self._add_node(node_id, comfy_json_node)
        return CLIP_VISION_OUTPUT(node_id, 0)

    def StyleModelApply(self, conditioning: CONDITIONING, style_model:
        STYLE_MODEL, clip_vision_output: CLIP_VISION_OUTPUT, strength:
        float, strength_type: str) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'style_model': to_comfy_input(style_model),
            'clip_vision_output': to_comfy_input(clip_vision_output),
            'strength': to_comfy_input(strength), 'strength_type':
            to_comfy_input(strength_type)}, 'class_type': 'StyleModelApply'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def unCLIPConditioning(self, conditioning: CONDITIONING,
        clip_vision_output: CLIP_VISION_OUTPUT, strength: float,
        noise_augmentation: float) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'clip_vision_output': to_comfy_input(
            clip_vision_output), 'strength': to_comfy_input(strength),
            'noise_augmentation': to_comfy_input(noise_augmentation)},
            'class_type': 'unCLIPConditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ControlNetApply(self, conditioning: CONDITIONING, control_net:
        CONTROL_NET, image: IMAGE, strength: float) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'control_net': to_comfy_input(control_net),
            'image': to_comfy_input(image), 'strength': to_comfy_input(
            strength)}, 'class_type': 'ControlNetApply'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ControlNetApplyAdvanced(self, positive: CONDITIONING, negative:
        CONDITIONING, control_net: CONTROL_NET, image: IMAGE, strength:
        float, start_percent: float, end_percent: float, vae: VAE) ->(
        CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'control_net':
            to_comfy_input(control_net), 'image': to_comfy_input(image),
            'strength': to_comfy_input(strength), 'start_percent':
            to_comfy_input(start_percent), 'end_percent': to_comfy_input(
            end_percent), 'vae': to_comfy_input(vae)}, 'class_type':
            'ControlNetApplyAdvanced'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def ControlNetLoader(self, control_net_name: str) ->CONTROL_NET:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'control_net_name': to_comfy_input(
            control_net_name)}, 'class_type': 'ControlNetLoader'}
        self._add_node(node_id, comfy_json_node)
        return CONTROL_NET(node_id, 0)

    def DiffControlNetLoader(self, model: MODEL, control_net_name: str
        ) ->CONTROL_NET:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'control_net_name': to_comfy_input(control_net_name)},
            'class_type': 'DiffControlNetLoader'}
        self._add_node(node_id, comfy_json_node)
        return CONTROL_NET(node_id, 0)

    def StyleModelLoader(self, style_model_name: str) ->STYLE_MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'style_model_name': to_comfy_input(
            style_model_name)}, 'class_type': 'StyleModelLoader'}
        self._add_node(node_id, comfy_json_node)
        return STYLE_MODEL(node_id, 0)

    def CLIPVisionLoader(self, clip_name: str) ->CLIP_VISION:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_name': to_comfy_input(clip_name
            )}, 'class_type': 'CLIPVisionLoader'}
        self._add_node(node_id, comfy_json_node)
        return CLIP_VISION(node_id, 0)

    def VAEDecodeTiled(self, samples: LATENT, vae: VAE, tile_size: int,
        overlap: int, temporal_size: int, temporal_overlap: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'vae': to_comfy_input(vae), 'tile_size': to_comfy_input(
            tile_size), 'overlap': to_comfy_input(overlap), 'temporal_size':
            to_comfy_input(temporal_size), 'temporal_overlap':
            to_comfy_input(temporal_overlap)}, 'class_type': 'VAEDecodeTiled'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def VAEEncodeTiled(self, pixels: IMAGE, vae: VAE, tile_size: int,
        overlap: int, temporal_size: int, temporal_overlap: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'pixels': to_comfy_input(pixels),
            'vae': to_comfy_input(vae), 'tile_size': to_comfy_input(
            tile_size), 'overlap': to_comfy_input(overlap), 'temporal_size':
            to_comfy_input(temporal_size), 'temporal_overlap':
            to_comfy_input(temporal_overlap)}, 'class_type': 'VAEEncodeTiled'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def unCLIPCheckpointLoader(self, ckpt_name: str) ->(MODEL, CLIP, VAE,
        CLIP_VISION):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'ckpt_name': to_comfy_input(ckpt_name
            )}, 'class_type': 'unCLIPCheckpointLoader'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP(node_id, 1), VAE(node_id, 2
            ), CLIP_VISION(node_id, 3)

    def GLIGENLoader(self, gligen_name: str) ->GLIGEN:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'gligen_name': to_comfy_input(
            gligen_name)}, 'class_type': 'GLIGENLoader'}
        self._add_node(node_id, comfy_json_node)
        return GLIGEN(node_id, 0)

    def GLIGENTextBoxApply(self, conditioning_to: CONDITIONING, clip: CLIP,
        gligen_textbox_model: GLIGEN, text: str, width: int, height: int, x:
        int, y: int) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning_to': to_comfy_input(
            conditioning_to), 'clip': to_comfy_input(clip),
            'gligen_textbox_model': to_comfy_input(gligen_textbox_model),
            'text': to_comfy_input(text), 'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'x': to_comfy_input(x), 'y':
            to_comfy_input(y)}, 'class_type': 'GLIGENTextBoxApply'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def InpaintModelConditioning(self, positive: CONDITIONING, negative:
        CONDITIONING, vae: VAE, pixels: IMAGE, mask: MASK, noise_mask: bool
        ) ->(CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'pixels': to_comfy_input(pixels), 'mask': to_comfy_input(
            mask), 'noise_mask': to_comfy_input(noise_mask)}, 'class_type':
            'InpaintModelConditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def CheckpointLoader(self, config_name: str, ckpt_name: str) ->(MODEL,
        CLIP, VAE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'config_name': to_comfy_input(
            config_name), 'ckpt_name': to_comfy_input(ckpt_name)},
            'class_type': 'CheckpointLoader'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP(node_id, 1), VAE(node_id, 2)

    def DiffusersLoader(self, model_path: str) ->(MODEL, CLIP, VAE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_path': to_comfy_input(
            model_path)}, 'class_type': 'DiffusersLoader'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP(node_id, 1), VAE(node_id, 2)

    def LoadLatent(self, latent: str) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'latent': to_comfy_input(latent)},
            'class_type': 'LoadLatent'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def SaveLatent(self, samples: LATENT, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'SaveLatent'}
        self._add_node(node_id, comfy_json_node)

    def ConditioningZeroOut(self, conditioning: CONDITIONING) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning)}, 'class_type': 'ConditioningZeroOut'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ConditioningSetTimestepRange(self, conditioning: CONDITIONING,
        start: float, end: float) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'start': to_comfy_input(start), 'end':
            to_comfy_input(end)}, 'class_type': 'ConditioningSetTimestepRange'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def LoraLoaderModelOnly(self, model: MODEL, lora_name: str,
        strength_model: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'lora_name': to_comfy_input(lora_name), 'strength_model':
            to_comfy_input(strength_model)}, 'class_type':
            'LoraLoaderModelOnly'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def LatentAdd(self, samples1: LATENT, samples2: LATENT) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples1': to_comfy_input(samples1),
            'samples2': to_comfy_input(samples2)}, 'class_type': 'LatentAdd'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentSubtract(self, samples1: LATENT, samples2: LATENT) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples1': to_comfy_input(samples1),
            'samples2': to_comfy_input(samples2)}, 'class_type':
            'LatentSubtract'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentMultiply(self, samples: LATENT, multiplier: float) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'multiplier': to_comfy_input(multiplier)}, 'class_type':
            'LatentMultiply'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentInterpolate(self, samples1: LATENT, samples2: LATENT, ratio:
        float) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples1': to_comfy_input(samples1),
            'samples2': to_comfy_input(samples2), 'ratio': to_comfy_input(
            ratio)}, 'class_type': 'LatentInterpolate'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentBatch(self, samples1: LATENT, samples2: LATENT) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples1': to_comfy_input(samples1),
            'samples2': to_comfy_input(samples2)}, 'class_type': 'LatentBatch'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentBatchSeedBehavior(self, samples: LATENT, seed_behavior: str
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'seed_behavior': to_comfy_input(seed_behavior)}, 'class_type':
            'LatentBatchSeedBehavior'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentApplyOperation(self, samples: LATENT, operation: LATENT_OPERATION
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'operation': to_comfy_input(operation)}, 'class_type':
            'LatentApplyOperation'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LatentApplyOperationCFG(self, model: MODEL, operation: LATENT_OPERATION
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'operation': to_comfy_input(operation)}, 'class_type':
            'LatentApplyOperationCFG'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def LatentOperationTonemapReinhard(self, multiplier: float
        ) ->LATENT_OPERATION:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'multiplier': to_comfy_input(
            multiplier)}, 'class_type': 'LatentOperationTonemapReinhard'}
        self._add_node(node_id, comfy_json_node)
        return LATENT_OPERATION(node_id, 0)

    def LatentOperationSharpen(self, sharpen_radius: int, sigma: float,
        alpha: float) ->LATENT_OPERATION:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sharpen_radius': to_comfy_input(
            sharpen_radius), 'sigma': to_comfy_input(sigma), 'alpha':
            to_comfy_input(alpha)}, 'class_type': 'LatentOperationSharpen'}
        self._add_node(node_id, comfy_json_node)
        return LATENT_OPERATION(node_id, 0)

    def HypernetworkLoader(self, model: MODEL, hypernetwork_name: str,
        strength: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'hypernetwork_name': to_comfy_input(hypernetwork_name),
            'strength': to_comfy_input(strength)}, 'class_type':
            'HypernetworkLoader'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def UpscaleModelLoader(self, model_name: str) ->UPSCALE_MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_name': to_comfy_input(
            model_name)}, 'class_type': 'UpscaleModelLoader'}
        self._add_node(node_id, comfy_json_node)
        return UPSCALE_MODEL(node_id, 0)

    def ImageUpscaleWithModel(self, upscale_model: UPSCALE_MODEL, image: IMAGE
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'upscale_model': to_comfy_input(
            upscale_model), 'image': to_comfy_input(image)}, 'class_type':
            'ImageUpscaleWithModel'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageBlend(self, image1: IMAGE, image2: IMAGE, blend_factor: float,
        blend_mode: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image1': to_comfy_input(image1),
            'image2': to_comfy_input(image2), 'blend_factor':
            to_comfy_input(blend_factor), 'blend_mode': to_comfy_input(
            blend_mode)}, 'class_type': 'ImageBlend'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageBlur(self, image: IMAGE, blur_radius: int, sigma: float) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'blur_radius': to_comfy_input(blur_radius), 'sigma':
            to_comfy_input(sigma)}, 'class_type': 'ImageBlur'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageQuantize(self, image: IMAGE, colors: int, dither: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'colors': to_comfy_input(colors), 'dither': to_comfy_input(
            dither)}, 'class_type': 'ImageQuantize'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageSharpen(self, image: IMAGE, sharpen_radius: int, sigma: float,
        alpha: float) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'sharpen_radius': to_comfy_input(sharpen_radius), 'sigma':
            to_comfy_input(sigma), 'alpha': to_comfy_input(alpha)},
            'class_type': 'ImageSharpen'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageScaleToTotalPixels(self, image: IMAGE, upscale_method: str,
        megapixels: float) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'upscale_method': to_comfy_input(upscale_method), 'megapixels':
            to_comfy_input(megapixels)}, 'class_type':
            'ImageScaleToTotalPixels'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LatentCompositeMasked(self, destination: LATENT, source: LATENT, x:
        int, y: int, resize_source: bool, mask: MASK) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'destination': to_comfy_input(
            destination), 'source': to_comfy_input(source), 'x':
            to_comfy_input(x), 'y': to_comfy_input(y), 'resize_source':
            to_comfy_input(resize_source), 'mask': to_comfy_input(mask)},
            'class_type': 'LatentCompositeMasked'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def ImageCompositeMasked(self, destination: IMAGE, source: IMAGE, x:
        int, y: int, resize_source: bool, mask: MASK) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'destination': to_comfy_input(
            destination), 'source': to_comfy_input(source), 'x':
            to_comfy_input(x), 'y': to_comfy_input(y), 'resize_source':
            to_comfy_input(resize_source), 'mask': to_comfy_input(mask)},
            'class_type': 'ImageCompositeMasked'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def MaskToImage(self, mask: MASK) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask)},
            'class_type': 'MaskToImage'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageToMask(self, image: IMAGE, channel: str) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'channel': to_comfy_input(channel)}, 'class_type': 'ImageToMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImageColorToMask(self, image: IMAGE, color: int) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'color': to_comfy_input(color)}, 'class_type': 'ImageColorToMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def SolidMask(self, value: float, width: int, height: int) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value),
            'width': to_comfy_input(width), 'height': to_comfy_input(height
            )}, 'class_type': 'SolidMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def InvertMask(self, mask: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask)},
            'class_type': 'InvertMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def CropMask(self, mask: MASK, x: int, y: int, width: int, height: int
        ) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask), 'x':
            to_comfy_input(x), 'y': to_comfy_input(y), 'width':
            to_comfy_input(width), 'height': to_comfy_input(height)},
            'class_type': 'CropMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def MaskComposite(self, destination: MASK, source: MASK, x: int, y: int,
        operation: str) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'destination': to_comfy_input(
            destination), 'source': to_comfy_input(source), 'x':
            to_comfy_input(x), 'y': to_comfy_input(y), 'operation':
            to_comfy_input(operation)}, 'class_type': 'MaskComposite'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def FeatherMask(self, mask: MASK, left: int, top: int, right: int,
        bottom: int) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask), 'left':
            to_comfy_input(left), 'top': to_comfy_input(top), 'right':
            to_comfy_input(right), 'bottom': to_comfy_input(bottom)},
            'class_type': 'FeatherMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def GrowMask(self, mask: MASK, expand: int, tapered_corners: bool) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask),
            'expand': to_comfy_input(expand), 'tapered_corners':
            to_comfy_input(tapered_corners)}, 'class_type': 'GrowMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ThresholdMask(self, mask: MASK, value: float) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask), 'value':
            to_comfy_input(value)}, 'class_type': 'ThresholdMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def MaskPreview(self, mask: MASK) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask)},
            'class_type': 'MaskPreview'}
        self._add_node(node_id, comfy_json_node)

    def PorterDuffImageComposite(self, source: IMAGE, source_alpha: MASK,
        destination: IMAGE, destination_alpha: MASK, mode: str) ->(IMAGE, MASK
        ):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'source': to_comfy_input(source),
            'source_alpha': to_comfy_input(source_alpha), 'destination':
            to_comfy_input(destination), 'destination_alpha':
            to_comfy_input(destination_alpha), 'mode': to_comfy_input(mode)
            }, 'class_type': 'PorterDuffImageComposite'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def SplitImageWithAlpha(self, image: IMAGE) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'SplitImageWithAlpha'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def JoinImageWithAlpha(self, image: IMAGE, alpha: MASK) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'alpha': to_comfy_input(alpha)}, 'class_type': 'JoinImageWithAlpha'
            }
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RebatchLatents(self, latents: LATENT, batch_size: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'latents': to_comfy_input(latents),
            'batch_size': to_comfy_input(batch_size)}, 'class_type':
            'RebatchLatents'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def RebatchImages(self, images: IMAGE, batch_size: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'batch_size': to_comfy_input(batch_size)}, 'class_type':
            'RebatchImages'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ModelMergeSimple(self, model1: MODEL, model2: MODEL, ratio: float
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'ratio': to_comfy_input(ratio
            )}, 'class_type': 'ModelMergeSimple'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeBlocks(self, model1: MODEL, model2: MODEL, input: float,
        middle: float, out: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'input': to_comfy_input(input
            ), 'middle': to_comfy_input(middle), 'out': to_comfy_input(out)
            }, 'class_type': 'ModelMergeBlocks'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeSubtract(self, model1: MODEL, model2: MODEL, multiplier:
        float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'multiplier': to_comfy_input(
            multiplier)}, 'class_type': 'ModelMergeSubtract'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeAdd(self, model1: MODEL, model2: MODEL) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2)}, 'class_type': 'ModelMergeAdd'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def CheckpointSave(self, model: MODEL, clip: CLIP, vae: VAE,
        filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'vae': to_comfy_input(vae),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'CheckpointSave'}
        self._add_node(node_id, comfy_json_node)

    def CLIPMergeSimple(self, clip1: CLIP, clip2: CLIP, ratio: float) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip1': to_comfy_input(clip1),
            'clip2': to_comfy_input(clip2), 'ratio': to_comfy_input(ratio)},
            'class_type': 'CLIPMergeSimple'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def CLIPMergeSubtract(self, clip1: CLIP, clip2: CLIP, multiplier: float
        ) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip1': to_comfy_input(clip1),
            'clip2': to_comfy_input(clip2), 'multiplier': to_comfy_input(
            multiplier)}, 'class_type': 'CLIPMergeSubtract'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def CLIPMergeAdd(self, clip1: CLIP, clip2: CLIP) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip1': to_comfy_input(clip1),
            'clip2': to_comfy_input(clip2)}, 'class_type': 'CLIPMergeAdd'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def CLIPSave(self, clip: CLIP, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'CLIPSave'}
        self._add_node(node_id, comfy_json_node)

    def VAESave(self, vae: VAE, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'vae': to_comfy_input(vae),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'VAESave'}
        self._add_node(node_id, comfy_json_node)

    def ModelSave(self, model: MODEL, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'ModelSave'}
        self._add_node(node_id, comfy_json_node)

    def TomePatchModel(self, model: MODEL, ratio: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'ratio': to_comfy_input(ratio)}, 'class_type': 'TomePatchModel'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def CLIPTextEncodeSDXLRefiner(self, ascore: float, width: int, height:
        int, text: str, clip: CLIP) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'ascore': to_comfy_input(ascore),
            'width': to_comfy_input(width), 'height': to_comfy_input(height
            ), 'text': to_comfy_input(text), 'clip': to_comfy_input(clip)},
            'class_type': 'CLIPTextEncodeSDXLRefiner'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def CLIPTextEncodeSDXL(self, clip: CLIP, width: int, height: int,
        crop_w: int, crop_h: int, target_width: int, target_height: int,
        text_g: str, text_l: str) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip), 'width':
            to_comfy_input(width), 'height': to_comfy_input(height),
            'crop_w': to_comfy_input(crop_w), 'crop_h': to_comfy_input(
            crop_h), 'target_width': to_comfy_input(target_width),
            'target_height': to_comfy_input(target_height), 'text_g':
            to_comfy_input(text_g), 'text_l': to_comfy_input(text_l)},
            'class_type': 'CLIPTextEncodeSDXL'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def Canny(self, image: IMAGE, low_threshold: float, high_threshold: float
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'low_threshold': to_comfy_input(low_threshold),
            'high_threshold': to_comfy_input(high_threshold)}, 'class_type':
            'Canny'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def FreeU(self, model: MODEL, b1: float, b2: float, s1: float, s2: float
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model), 'b1':
            to_comfy_input(b1), 'b2': to_comfy_input(b2), 's1':
            to_comfy_input(s1), 's2': to_comfy_input(s2)}, 'class_type':
            'FreeU'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def FreeU_V2(self, model: MODEL, b1: float, b2: float, s1: float, s2: float
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model), 'b1':
            to_comfy_input(b1), 'b2': to_comfy_input(b2), 's1':
            to_comfy_input(s1), 's2': to_comfy_input(s2)}, 'class_type':
            'FreeU_V2'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def SamplerCustom(self, model: MODEL, add_noise: bool, noise_seed: int,
        cfg: float, positive: CONDITIONING, negative: CONDITIONING, sampler:
        SAMPLER, sigmas: SIGMAS, latent_image: LATENT) ->(LATENT, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'add_noise': to_comfy_input(add_noise), 'noise_seed':
            to_comfy_input(noise_seed), 'cfg': to_comfy_input(cfg),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'sampler': to_comfy_input(sampler),
            'sigmas': to_comfy_input(sigmas), 'latent_image':
            to_comfy_input(latent_image)}, 'class_type': 'SamplerCustom'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0), LATENT(node_id, 1)

    def BasicScheduler(self, model: MODEL, scheduler: str, steps: int,
        denoise: float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'scheduler': to_comfy_input(scheduler), 'steps': to_comfy_input
            (steps), 'denoise': to_comfy_input(denoise)}, 'class_type':
            'BasicScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def KarrasScheduler(self, steps: int, sigma_max: float, sigma_min:
        float, rho: float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'steps': to_comfy_input(steps),
            'sigma_max': to_comfy_input(sigma_max), 'sigma_min':
            to_comfy_input(sigma_min), 'rho': to_comfy_input(rho)},
            'class_type': 'KarrasScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def ExponentialScheduler(self, steps: int, sigma_max: float, sigma_min:
        float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'steps': to_comfy_input(steps),
            'sigma_max': to_comfy_input(sigma_max), 'sigma_min':
            to_comfy_input(sigma_min)}, 'class_type': 'ExponentialScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def PolyexponentialScheduler(self, steps: int, sigma_max: float,
        sigma_min: float, rho: float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'steps': to_comfy_input(steps),
            'sigma_max': to_comfy_input(sigma_max), 'sigma_min':
            to_comfy_input(sigma_min), 'rho': to_comfy_input(rho)},
            'class_type': 'PolyexponentialScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def LaplaceScheduler(self, steps: int, sigma_max: float, sigma_min:
        float, mu: float, beta: float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'steps': to_comfy_input(steps),
            'sigma_max': to_comfy_input(sigma_max), 'sigma_min':
            to_comfy_input(sigma_min), 'mu': to_comfy_input(mu), 'beta':
            to_comfy_input(beta)}, 'class_type': 'LaplaceScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def VPScheduler(self, steps: int, beta_d: float, beta_min: float, eps_s:
        float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'steps': to_comfy_input(steps),
            'beta_d': to_comfy_input(beta_d), 'beta_min': to_comfy_input(
            beta_min), 'eps_s': to_comfy_input(eps_s)}, 'class_type':
            'VPScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def BetaSamplingScheduler(self, model: MODEL, steps: int, alpha: float,
        beta: float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'steps': to_comfy_input(steps), 'alpha': to_comfy_input(alpha),
            'beta': to_comfy_input(beta)}, 'class_type':
            'BetaSamplingScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def SDTurboScheduler(self, model: MODEL, steps: int, denoise: float
        ) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'steps': to_comfy_input(steps), 'denoise': to_comfy_input(
            denoise)}, 'class_type': 'SDTurboScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def KSamplerSelect(self, sampler_name: str) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sampler_name': to_comfy_input(
            sampler_name)}, 'class_type': 'KSamplerSelect'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerEulerAncestral(self, eta: float, s_noise: float) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'eta': to_comfy_input(eta), 's_noise':
            to_comfy_input(s_noise)}, 'class_type': 'SamplerEulerAncestral'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerEulerAncestralCFGPP(self, eta: float, s_noise: float) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'eta': to_comfy_input(eta), 's_noise':
            to_comfy_input(s_noise)}, 'class_type':
            'SamplerEulerAncestralCFGPP'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerLMS(self, order: int) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'order': to_comfy_input(order)},
            'class_type': 'SamplerLMS'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerDPMPP_3M_SDE(self, eta: float, s_noise: float, noise_device: str
        ) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'eta': to_comfy_input(eta), 's_noise':
            to_comfy_input(s_noise), 'noise_device': to_comfy_input(
            noise_device)}, 'class_type': 'SamplerDPMPP_3M_SDE'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerDPMPP_2M_SDE(self, solver_type: str, eta: float, s_noise:
        float, noise_device: str) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'solver_type': to_comfy_input(
            solver_type), 'eta': to_comfy_input(eta), 's_noise':
            to_comfy_input(s_noise), 'noise_device': to_comfy_input(
            noise_device)}, 'class_type': 'SamplerDPMPP_2M_SDE'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerDPMPP_SDE(self, eta: float, s_noise: float, r: float,
        noise_device: str) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'eta': to_comfy_input(eta), 's_noise':
            to_comfy_input(s_noise), 'r': to_comfy_input(r), 'noise_device':
            to_comfy_input(noise_device)}, 'class_type': 'SamplerDPMPP_SDE'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerDPMPP_2S_Ancestral(self, eta: float, s_noise: float) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'eta': to_comfy_input(eta), 's_noise':
            to_comfy_input(s_noise)}, 'class_type': 'SamplerDPMPP_2S_Ancestral'
            }
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerDPMAdaptative(self, order: int, rtol: float, atol: float,
        h_init: float, pcoeff: float, icoeff: float, dcoeff: float,
        accept_safety: float, eta: float, s_noise: float) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'order': to_comfy_input(order),
            'rtol': to_comfy_input(rtol), 'atol': to_comfy_input(atol),
            'h_init': to_comfy_input(h_init), 'pcoeff': to_comfy_input(
            pcoeff), 'icoeff': to_comfy_input(icoeff), 'dcoeff':
            to_comfy_input(dcoeff), 'accept_safety': to_comfy_input(
            accept_safety), 'eta': to_comfy_input(eta), 's_noise':
            to_comfy_input(s_noise)}, 'class_type': 'SamplerDPMAdaptative'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerER_SDE(self, solver_type: COMBO, max_stage: int, eta: float,
        s_noise: float) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'solver_type': to_comfy_input(
            solver_type), 'max_stage': to_comfy_input(max_stage), 'eta':
            to_comfy_input(eta), 's_noise': to_comfy_input(s_noise)},
            'class_type': 'SamplerER_SDE'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerSASolver(self, model: MODEL, eta: float, sde_start_percent:
        float, sde_end_percent: float, s_noise: float, predictor_order: int,
        corrector_order: int, use_pece: bool, simple_order_2: bool) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model), 'eta':
            to_comfy_input(eta), 'sde_start_percent': to_comfy_input(
            sde_start_percent), 'sde_end_percent': to_comfy_input(
            sde_end_percent), 's_noise': to_comfy_input(s_noise),
            'predictor_order': to_comfy_input(predictor_order),
            'corrector_order': to_comfy_input(corrector_order), 'use_pece':
            to_comfy_input(use_pece), 'simple_order_2': to_comfy_input(
            simple_order_2)}, 'class_type': 'SamplerSASolver'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SplitSigmas(self, sigmas: SIGMAS, step: int) ->(SIGMAS, SIGMAS):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sigmas': to_comfy_input(sigmas),
            'step': to_comfy_input(step)}, 'class_type': 'SplitSigmas'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0), SIGMAS(node_id, 1)

    def SplitSigmasDenoise(self, sigmas: SIGMAS, denoise: float) ->(SIGMAS,
        SIGMAS):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sigmas': to_comfy_input(sigmas),
            'denoise': to_comfy_input(denoise)}, 'class_type':
            'SplitSigmasDenoise'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0), SIGMAS(node_id, 1)

    def FlipSigmas(self, sigmas: SIGMAS) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sigmas': to_comfy_input(sigmas)},
            'class_type': 'FlipSigmas'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def SetFirstSigma(self, sigmas: SIGMAS, sigma: float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sigmas': to_comfy_input(sigmas),
            'sigma': to_comfy_input(sigma)}, 'class_type': 'SetFirstSigma'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def ExtendIntermediateSigmas(self, sigmas: SIGMAS, steps: int,
        start_at_sigma: float, end_at_sigma: float, spacing: str) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sigmas': to_comfy_input(sigmas),
            'steps': to_comfy_input(steps), 'start_at_sigma':
            to_comfy_input(start_at_sigma), 'end_at_sigma': to_comfy_input(
            end_at_sigma), 'spacing': to_comfy_input(spacing)},
            'class_type': 'ExtendIntermediateSigmas'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def SamplingPercentToSigma(self, model: MODEL, sampling_percent: float,
        return_actual_sigma: bool) ->FloatNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'sampling_percent': to_comfy_input(sampling_percent),
            'return_actual_sigma': to_comfy_input(return_actual_sigma)},
            'class_type': 'SamplingPercentToSigma'}
        self._add_node(node_id, comfy_json_node)
        return FloatNodeOutput(node_id, 0)

    def CFGGuider(self, model: MODEL, positive: CONDITIONING, negative:
        CONDITIONING, cfg: float) ->GUIDER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'cfg': to_comfy_input(cfg)},
            'class_type': 'CFGGuider'}
        self._add_node(node_id, comfy_json_node)
        return GUIDER(node_id, 0)

    def DualCFGGuider(self, model: MODEL, cond1: CONDITIONING, cond2:
        CONDITIONING, negative: CONDITIONING, cfg_conds: float,
        cfg_cond2_negative: float, style: str) ->GUIDER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'cond1': to_comfy_input(cond1), 'cond2': to_comfy_input(cond2),
            'negative': to_comfy_input(negative), 'cfg_conds':
            to_comfy_input(cfg_conds), 'cfg_cond2_negative': to_comfy_input
            (cfg_cond2_negative), 'style': to_comfy_input(style)},
            'class_type': 'DualCFGGuider'}
        self._add_node(node_id, comfy_json_node)
        return GUIDER(node_id, 0)

    def BasicGuider(self, model: MODEL, conditioning: CONDITIONING) ->GUIDER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'conditioning': to_comfy_input(conditioning)}, 'class_type':
            'BasicGuider'}
        self._add_node(node_id, comfy_json_node)
        return GUIDER(node_id, 0)

    def RandomNoise(self, noise_seed: int) ->NOISE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'noise_seed': to_comfy_input(
            noise_seed)}, 'class_type': 'RandomNoise'}
        self._add_node(node_id, comfy_json_node)
        return NOISE(node_id, 0)

    def DisableNoise(self) ->NOISE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {}, 'class_type': 'DisableNoise'}
        self._add_node(node_id, comfy_json_node)
        return NOISE(node_id, 0)

    def AddNoise(self, model: MODEL, noise: NOISE, sigmas: SIGMAS,
        latent_image: LATENT) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'noise': to_comfy_input(noise), 'sigmas': to_comfy_input(sigmas
            ), 'latent_image': to_comfy_input(latent_image)}, 'class_type':
            'AddNoise'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def SamplerCustomAdvanced(self, noise: NOISE, guider: GUIDER, sampler:
        SAMPLER, sigmas: SIGMAS, latent_image: LATENT) ->(LATENT, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'noise': to_comfy_input(noise),
            'guider': to_comfy_input(guider), 'sampler': to_comfy_input(
            sampler), 'sigmas': to_comfy_input(sigmas), 'latent_image':
            to_comfy_input(latent_image)}, 'class_type':
            'SamplerCustomAdvanced'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0), LATENT(node_id, 1)

    def HyperTile(self, model: MODEL, tile_size: int, swap_size: int,
        max_depth: int, scale_depth: bool) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'tile_size': to_comfy_input(tile_size), 'swap_size':
            to_comfy_input(swap_size), 'max_depth': to_comfy_input(
            max_depth), 'scale_depth': to_comfy_input(scale_depth)},
            'class_type': 'HyperTile'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelSamplingDiscrete(self, model: MODEL, sampling: str, zsnr: bool
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'sampling': to_comfy_input(sampling), 'zsnr': to_comfy_input(
            zsnr)}, 'class_type': 'ModelSamplingDiscrete'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelSamplingContinuousEDM(self, model: MODEL, sampling: str,
        sigma_max: float, sigma_min: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'sampling': to_comfy_input(sampling), 'sigma_max':
            to_comfy_input(sigma_max), 'sigma_min': to_comfy_input(
            sigma_min)}, 'class_type': 'ModelSamplingContinuousEDM'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelSamplingContinuousV(self, model: MODEL, sampling: str,
        sigma_max: float, sigma_min: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'sampling': to_comfy_input(sampling), 'sigma_max':
            to_comfy_input(sigma_max), 'sigma_min': to_comfy_input(
            sigma_min)}, 'class_type': 'ModelSamplingContinuousV'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelSamplingStableCascade(self, model: MODEL, shift: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'shift': to_comfy_input(shift)}, 'class_type':
            'ModelSamplingStableCascade'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelSamplingSD3(self, model: MODEL, shift: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'shift': to_comfy_input(shift)}, 'class_type': 'ModelSamplingSD3'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelSamplingAuraFlow(self, model: MODEL, shift: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'shift': to_comfy_input(shift)}, 'class_type':
            'ModelSamplingAuraFlow'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelSamplingFlux(self, model: MODEL, max_shift: float, base_shift:
        float, width: int, height: int) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'max_shift': to_comfy_input(max_shift), 'base_shift':
            to_comfy_input(base_shift), 'width': to_comfy_input(width),
            'height': to_comfy_input(height)}, 'class_type':
            'ModelSamplingFlux'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def RescaleCFG(self, model: MODEL, multiplier: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'multiplier': to_comfy_input(multiplier)}, 'class_type':
            'RescaleCFG'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelComputeDtype(self, model: MODEL, dtype: str) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'dtype': to_comfy_input(dtype)}, 'class_type': 'ModelComputeDtype'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def PatchModelAddDownscale(self, model: MODEL, block_number: int,
        downscale_factor: float, start_percent: float, end_percent: float,
        downscale_after_skip: bool, downscale_method: str, upscale_method: str
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'block_number': to_comfy_input(block_number),
            'downscale_factor': to_comfy_input(downscale_factor),
            'start_percent': to_comfy_input(start_percent), 'end_percent':
            to_comfy_input(end_percent), 'downscale_after_skip':
            to_comfy_input(downscale_after_skip), 'downscale_method':
            to_comfy_input(downscale_method), 'upscale_method':
            to_comfy_input(upscale_method)}, 'class_type':
            'PatchModelAddDownscale'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ImageCrop(self, image: IMAGE, width: int, height: int, x: int, y: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'width': to_comfy_input(width), 'height': to_comfy_input(height
            ), 'x': to_comfy_input(x), 'y': to_comfy_input(y)},
            'class_type': 'ImageCrop'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RepeatImageBatch(self, image: IMAGE, amount: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'amount': to_comfy_input(amount)}, 'class_type': 'RepeatImageBatch'
            }
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageFromBatch(self, image: IMAGE, batch_index: int, length: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'batch_index': to_comfy_input(batch_index), 'length':
            to_comfy_input(length)}, 'class_type': 'ImageFromBatch'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageAddNoise(self, image: IMAGE, seed: int, strength: float) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'seed': to_comfy_input(seed), 'strength': to_comfy_input(
            strength)}, 'class_type': 'ImageAddNoise'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SaveAnimatedWEBP(self, images: IMAGE, filename_prefix: str, fps:
        float, lossless: bool, quality: int, method: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'filename_prefix': to_comfy_input(filename_prefix), 'fps':
            to_comfy_input(fps), 'lossless': to_comfy_input(lossless),
            'quality': to_comfy_input(quality), 'method': to_comfy_input(
            method)}, 'class_type': 'SaveAnimatedWEBP'}
        self._add_node(node_id, comfy_json_node)

    def SaveAnimatedPNG(self, images: IMAGE, filename_prefix: str, fps:
        float, compress_level: int) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'filename_prefix': to_comfy_input(filename_prefix), 'fps':
            to_comfy_input(fps), 'compress_level': to_comfy_input(
            compress_level)}, 'class_type': 'SaveAnimatedPNG'}
        self._add_node(node_id, comfy_json_node)

    def SaveSVGNode(self, svg: SVG, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'svg': to_comfy_input(svg),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'SaveSVGNode'}
        self._add_node(node_id, comfy_json_node)

    def ImageStitch(self, image1: IMAGE, direction: str, match_image_size:
        bool, spacing_width: int, spacing_color: str, image2: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image1': to_comfy_input(image1),
            'direction': to_comfy_input(direction), 'match_image_size':
            to_comfy_input(match_image_size), 'spacing_width':
            to_comfy_input(spacing_width), 'spacing_color': to_comfy_input(
            spacing_color), 'image2': to_comfy_input(image2)}, 'class_type':
            'ImageStitch'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ResizeAndPadImage(self, image: IMAGE, target_width: int,
        target_height: int, padding_color: str, interpolation: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'target_width': to_comfy_input(target_width), 'target_height':
            to_comfy_input(target_height), 'padding_color': to_comfy_input(
            padding_color), 'interpolation': to_comfy_input(interpolation)},
            'class_type': 'ResizeAndPadImage'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def GetImageSize(self, image: IMAGE) ->(IntNodeOutput, IntNodeOutput,
        IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'GetImageSize'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0), IntNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2)

    def ImageRotate(self, image: IMAGE, rotation: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'rotation': to_comfy_input(rotation)}, 'class_type': 'ImageRotate'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageFlip(self, image: IMAGE, flip_method: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'flip_method': to_comfy_input(flip_method)}, 'class_type':
            'ImageFlip'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageOnlyCheckpointLoader(self, ckpt_name: str) ->(MODEL,
        CLIP_VISION, VAE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'ckpt_name': to_comfy_input(ckpt_name
            )}, 'class_type': 'ImageOnlyCheckpointLoader'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP_VISION(node_id, 1), VAE(node_id, 2)

    def SVD_img2vid_Conditioning(self, clip_vision: CLIP_VISION, init_image:
        IMAGE, vae: VAE, width: int, height: int, video_frames: int,
        motion_bucket_id: int, fps: int, augmentation_level: float) ->(
        CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_vision': to_comfy_input(
            clip_vision), 'init_image': to_comfy_input(init_image), 'vae':
            to_comfy_input(vae), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height), 'video_frames': to_comfy_input(
            video_frames), 'motion_bucket_id': to_comfy_input(
            motion_bucket_id), 'fps': to_comfy_input(fps),
            'augmentation_level': to_comfy_input(augmentation_level)},
            'class_type': 'SVD_img2vid_Conditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def VideoLinearCFGGuidance(self, model: MODEL, min_cfg: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'min_cfg': to_comfy_input(min_cfg)}, 'class_type':
            'VideoLinearCFGGuidance'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def VideoTriangleCFGGuidance(self, model: MODEL, min_cfg: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'min_cfg': to_comfy_input(min_cfg)}, 'class_type':
            'VideoTriangleCFGGuidance'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ImageOnlyCheckpointSave(self, model: MODEL, clip_vision:
        CLIP_VISION, vae: VAE, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'clip_vision': to_comfy_input(clip_vision), 'vae':
            to_comfy_input(vae), 'filename_prefix': to_comfy_input(
            filename_prefix)}, 'class_type': 'ImageOnlyCheckpointSave'}
        self._add_node(node_id, comfy_json_node)

    def ConditioningSetAreaPercentageVideo(self, conditioning: CONDITIONING,
        width: float, height: float, temporal: float, x: float, y: float, z:
        float, strength: float) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height), 'temporal': to_comfy_input(temporal),
            'x': to_comfy_input(x), 'y': to_comfy_input(y), 'z':
            to_comfy_input(z), 'strength': to_comfy_input(strength)},
            'class_type': 'ConditioningSetAreaPercentageVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def TrainLoraNode(self, model: MODEL, latents: LATENT, positive:
        CONDITIONING, batch_size: int, steps: int, learning_rate: float,
        rank: int, optimizer: str, loss_function: str, seed: int,
        training_dtype: str, lora_dtype: str, existing_lora: str) ->(MODEL,
        LORA_MODEL, LOSS_MAP, IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'latents': to_comfy_input(latents), 'positive': to_comfy_input(
            positive), 'batch_size': to_comfy_input(batch_size), 'steps':
            to_comfy_input(steps), 'learning_rate': to_comfy_input(
            learning_rate), 'rank': to_comfy_input(rank), 'optimizer':
            to_comfy_input(optimizer), 'loss_function': to_comfy_input(
            loss_function), 'seed': to_comfy_input(seed), 'training_dtype':
            to_comfy_input(training_dtype), 'lora_dtype': to_comfy_input(
            lora_dtype), 'existing_lora': to_comfy_input(existing_lora)},
            'class_type': 'TrainLoraNode'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), LORA_MODEL(node_id, 1), LOSS_MAP(node_id, 2
            ), IntNodeOutput(node_id, 3)

    def SaveLoRANode(self, lora: LORA_MODEL, prefix: str, steps: int) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'lora': to_comfy_input(lora),
            'prefix': to_comfy_input(prefix), 'steps': to_comfy_input(steps
            )}, 'class_type': 'SaveLoRANode'}
        self._add_node(node_id, comfy_json_node)

    def LoraModelLoader(self, model: MODEL, lora: LORA_MODEL,
        strength_model: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'lora': to_comfy_input(lora), 'strength_model': to_comfy_input(
            strength_model)}, 'class_type': 'LoraModelLoader'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def LoadImageSetFromFolderNode(self, folder: str, resize_method: str
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'folder': to_comfy_input(folder),
            'resize_method': to_comfy_input(resize_method)}, 'class_type':
            'LoadImageSetFromFolderNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LoadImageTextSetFromFolderNode(self, folder: str, clip: CLIP,
        resize_method: str, width: int, height: int) ->(IMAGE, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'folder': to_comfy_input(folder),
            'clip': to_comfy_input(clip), 'resize_method': to_comfy_input(
            resize_method), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height)}, 'class_type':
            'LoadImageTextSetFromFolderNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), CONDITIONING(node_id, 1)

    def LossGraphNode(self, loss: LOSS_MAP, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'loss': to_comfy_input(loss),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'LossGraphNode'}
        self._add_node(node_id, comfy_json_node)

    def SelfAttentionGuidance(self, model: MODEL, scale: float, blur_sigma:
        float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'scale': to_comfy_input(scale), 'blur_sigma': to_comfy_input(
            blur_sigma)}, 'class_type': 'SelfAttentionGuidance'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def PerpNeg(self, model: MODEL, empty_conditioning: CONDITIONING,
        neg_scale: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'empty_conditioning': to_comfy_input(empty_conditioning),
            'neg_scale': to_comfy_input(neg_scale)}, 'class_type': 'PerpNeg'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def PerpNegGuider(self, model: MODEL, positive: CONDITIONING, negative:
        CONDITIONING, empty_conditioning: CONDITIONING, cfg: float,
        neg_scale: float) ->GUIDER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'empty_conditioning': to_comfy_input(
            empty_conditioning), 'cfg': to_comfy_input(cfg), 'neg_scale':
            to_comfy_input(neg_scale)}, 'class_type': 'PerpNegGuider'}
        self._add_node(node_id, comfy_json_node)
        return GUIDER(node_id, 0)

    def StableZero123_Conditioning(self, clip_vision: CLIP_VISION,
        init_image: IMAGE, vae: VAE, width: int, height: int, batch_size:
        int, elevation: float, azimuth: float) ->(CONDITIONING,
        CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_vision': to_comfy_input(
            clip_vision), 'init_image': to_comfy_input(init_image), 'vae':
            to_comfy_input(vae), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height), 'batch_size': to_comfy_input(batch_size
            ), 'elevation': to_comfy_input(elevation), 'azimuth':
            to_comfy_input(azimuth)}, 'class_type':
            'StableZero123_Conditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def StableZero123_Conditioning_Batched(self, clip_vision: CLIP_VISION,
        init_image: IMAGE, vae: VAE, width: int, height: int, batch_size:
        int, elevation: float, azimuth: float, elevation_batch_increment:
        float, azimuth_batch_increment: float) ->(CONDITIONING,
        CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_vision': to_comfy_input(
            clip_vision), 'init_image': to_comfy_input(init_image), 'vae':
            to_comfy_input(vae), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height), 'batch_size': to_comfy_input(batch_size
            ), 'elevation': to_comfy_input(elevation), 'azimuth':
            to_comfy_input(azimuth), 'elevation_batch_increment':
            to_comfy_input(elevation_batch_increment),
            'azimuth_batch_increment': to_comfy_input(
            azimuth_batch_increment)}, 'class_type':
            'StableZero123_Conditioning_Batched'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def SV3D_Conditioning(self, clip_vision: CLIP_VISION, init_image: IMAGE,
        vae: VAE, width: int, height: int, video_frames: int, elevation: float
        ) ->(CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_vision': to_comfy_input(
            clip_vision), 'init_image': to_comfy_input(init_image), 'vae':
            to_comfy_input(vae), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height), 'video_frames': to_comfy_input(
            video_frames), 'elevation': to_comfy_input(elevation)},
            'class_type': 'SV3D_Conditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def SD_4XUpscale_Conditioning(self, images: IMAGE, positive:
        CONDITIONING, negative: CONDITIONING, scale_ratio: float,
        noise_augmentation: float) ->(CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'scale_ratio': to_comfy_input(
            scale_ratio), 'noise_augmentation': to_comfy_input(
            noise_augmentation)}, 'class_type': 'SD_4XUpscale_Conditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def PhotoMakerLoader(self, photomaker_model_name: str) ->PHOTOMAKER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'photomaker_model_name':
            to_comfy_input(photomaker_model_name)}, 'class_type':
            'PhotoMakerLoader'}
        self._add_node(node_id, comfy_json_node)
        return PHOTOMAKER(node_id, 0)

    def PhotoMakerEncode(self, photomaker: PHOTOMAKER, image: IMAGE, clip:
        CLIP, text: str) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'photomaker': to_comfy_input(
            photomaker), 'image': to_comfy_input(image), 'clip':
            to_comfy_input(clip), 'text': to_comfy_input(text)},
            'class_type': 'PhotoMakerEncode'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def CLIPTextEncodePixArtAlpha(self, width: int, height: int, text: str,
        clip: CLIP) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'text': to_comfy_input(text),
            'clip': to_comfy_input(clip)}, 'class_type':
            'CLIPTextEncodePixArtAlpha'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def CLIPTextEncodeControlnet(self, clip: CLIP, conditioning:
        CONDITIONING, text: str) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'conditioning': to_comfy_input(conditioning), 'text':
            to_comfy_input(text)}, 'class_type': 'CLIPTextEncodeControlnet'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def T5TokenizerOptions(self, clip: CLIP, min_padding: int, min_length: int
        ) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'min_padding': to_comfy_input(min_padding), 'min_length':
            to_comfy_input(min_length)}, 'class_type': 'T5TokenizerOptions'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def Morphology(self, image: IMAGE, operation: str, kernel_size: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'operation': to_comfy_input(operation), 'kernel_size':
            to_comfy_input(kernel_size)}, 'class_type': 'Morphology'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageRGBToYUV(self, image: IMAGE) ->(IMAGE, IMAGE, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'ImageRGBToYUV'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), IMAGE(node_id, 1), IMAGE(node_id, 2)

    def ImageYUVToRGB(self, Y: IMAGE, U: IMAGE, V: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'Y': to_comfy_input(Y), 'U':
            to_comfy_input(U), 'V': to_comfy_input(V)}, 'class_type':
            'ImageYUVToRGB'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def StableCascade_EmptyLatentImage(self, width: int, height: int,
        compression: int, batch_size: int) ->(LATENT, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'compression': to_comfy_input
            (compression), 'batch_size': to_comfy_input(batch_size)},
            'class_type': 'StableCascade_EmptyLatentImage'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0), LATENT(node_id, 1)

    def StableCascade_StageB_Conditioning(self, conditioning: CONDITIONING,
        stage_c: LATENT) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'stage_c': to_comfy_input(stage_c)},
            'class_type': 'StableCascade_StageB_Conditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def StableCascade_StageC_VAEEncode(self, image: IMAGE, vae: VAE,
        compression: int) ->(LATENT, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image), 'vae':
            to_comfy_input(vae), 'compression': to_comfy_input(compression)
            }, 'class_type': 'StableCascade_StageC_VAEEncode'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0), LATENT(node_id, 1)

    def StableCascade_SuperResolutionControlnet(self, image: IMAGE, vae: VAE
        ) ->(IMAGE, LATENT, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image), 'vae':
            to_comfy_input(vae)}, 'class_type':
            'StableCascade_SuperResolutionControlnet'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), LATENT(node_id, 1), LATENT(node_id, 2)

    def DifferentialDiffusion(self, model: MODEL) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model)},
            'class_type': 'DifferentialDiffusion'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def InstructPixToPixConditioning(self, positive: CONDITIONING, negative:
        CONDITIONING, vae: VAE, pixels: IMAGE) ->(CONDITIONING,
        CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'pixels': to_comfy_input(pixels)}, 'class_type':
            'InstructPixToPixConditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def ModelMergeSD1(self, model1: MODEL, model2: MODEL, time_embed: float,
        label_emb: float, input_blocks_0: float, input_blocks_1: float,
        input_blocks_2: float, input_blocks_3: float, input_blocks_4: float,
        input_blocks_5: float, input_blocks_6: float, input_blocks_7: float,
        input_blocks_8: float, input_blocks_9: float, input_blocks_10:
        float, input_blocks_11: float, middle_block_0: float,
        middle_block_1: float, middle_block_2: float, output_blocks_0:
        float, output_blocks_1: float, output_blocks_2: float,
        output_blocks_3: float, output_blocks_4: float, output_blocks_5:
        float, output_blocks_6: float, output_blocks_7: float,
        output_blocks_8: float, output_blocks_9: float, output_blocks_10:
        float, output_blocks_11: float, out: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'time_embed.': to_comfy_input
            (time_embed), 'label_emb.': to_comfy_input(label_emb),
            'input_blocks.0.': to_comfy_input(input_blocks_0),
            'input_blocks.1.': to_comfy_input(input_blocks_1),
            'input_blocks.2.': to_comfy_input(input_blocks_2),
            'input_blocks.3.': to_comfy_input(input_blocks_3),
            'input_blocks.4.': to_comfy_input(input_blocks_4),
            'input_blocks.5.': to_comfy_input(input_blocks_5),
            'input_blocks.6.': to_comfy_input(input_blocks_6),
            'input_blocks.7.': to_comfy_input(input_blocks_7),
            'input_blocks.8.': to_comfy_input(input_blocks_8),
            'input_blocks.9.': to_comfy_input(input_blocks_9),
            'input_blocks.10.': to_comfy_input(input_blocks_10),
            'input_blocks.11.': to_comfy_input(input_blocks_11),
            'middle_block.0.': to_comfy_input(middle_block_0),
            'middle_block.1.': to_comfy_input(middle_block_1),
            'middle_block.2.': to_comfy_input(middle_block_2),
            'output_blocks.0.': to_comfy_input(output_blocks_0),
            'output_blocks.1.': to_comfy_input(output_blocks_1),
            'output_blocks.2.': to_comfy_input(output_blocks_2),
            'output_blocks.3.': to_comfy_input(output_blocks_3),
            'output_blocks.4.': to_comfy_input(output_blocks_4),
            'output_blocks.5.': to_comfy_input(output_blocks_5),
            'output_blocks.6.': to_comfy_input(output_blocks_6),
            'output_blocks.7.': to_comfy_input(output_blocks_7),
            'output_blocks.8.': to_comfy_input(output_blocks_8),
            'output_blocks.9.': to_comfy_input(output_blocks_9),
            'output_blocks.10.': to_comfy_input(output_blocks_10),
            'output_blocks.11.': to_comfy_input(output_blocks_11), 'out.':
            to_comfy_input(out)}, 'class_type': 'ModelMergeSD1'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeSD2(self, model1: MODEL, model2: MODEL, time_embed: float,
        label_emb: float, input_blocks_0: float, input_blocks_1: float,
        input_blocks_2: float, input_blocks_3: float, input_blocks_4: float,
        input_blocks_5: float, input_blocks_6: float, input_blocks_7: float,
        input_blocks_8: float, input_blocks_9: float, input_blocks_10:
        float, input_blocks_11: float, middle_block_0: float,
        middle_block_1: float, middle_block_2: float, output_blocks_0:
        float, output_blocks_1: float, output_blocks_2: float,
        output_blocks_3: float, output_blocks_4: float, output_blocks_5:
        float, output_blocks_6: float, output_blocks_7: float,
        output_blocks_8: float, output_blocks_9: float, output_blocks_10:
        float, output_blocks_11: float, out: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'time_embed.': to_comfy_input
            (time_embed), 'label_emb.': to_comfy_input(label_emb),
            'input_blocks.0.': to_comfy_input(input_blocks_0),
            'input_blocks.1.': to_comfy_input(input_blocks_1),
            'input_blocks.2.': to_comfy_input(input_blocks_2),
            'input_blocks.3.': to_comfy_input(input_blocks_3),
            'input_blocks.4.': to_comfy_input(input_blocks_4),
            'input_blocks.5.': to_comfy_input(input_blocks_5),
            'input_blocks.6.': to_comfy_input(input_blocks_6),
            'input_blocks.7.': to_comfy_input(input_blocks_7),
            'input_blocks.8.': to_comfy_input(input_blocks_8),
            'input_blocks.9.': to_comfy_input(input_blocks_9),
            'input_blocks.10.': to_comfy_input(input_blocks_10),
            'input_blocks.11.': to_comfy_input(input_blocks_11),
            'middle_block.0.': to_comfy_input(middle_block_0),
            'middle_block.1.': to_comfy_input(middle_block_1),
            'middle_block.2.': to_comfy_input(middle_block_2),
            'output_blocks.0.': to_comfy_input(output_blocks_0),
            'output_blocks.1.': to_comfy_input(output_blocks_1),
            'output_blocks.2.': to_comfy_input(output_blocks_2),
            'output_blocks.3.': to_comfy_input(output_blocks_3),
            'output_blocks.4.': to_comfy_input(output_blocks_4),
            'output_blocks.5.': to_comfy_input(output_blocks_5),
            'output_blocks.6.': to_comfy_input(output_blocks_6),
            'output_blocks.7.': to_comfy_input(output_blocks_7),
            'output_blocks.8.': to_comfy_input(output_blocks_8),
            'output_blocks.9.': to_comfy_input(output_blocks_9),
            'output_blocks.10.': to_comfy_input(output_blocks_10),
            'output_blocks.11.': to_comfy_input(output_blocks_11), 'out.':
            to_comfy_input(out)}, 'class_type': 'ModelMergeSD2'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeSDXL(self, model1: MODEL, model2: MODEL, time_embed:
        float, label_emb: float, input_blocks_0: float, input_blocks_1:
        float, input_blocks_2: float, input_blocks_3: float, input_blocks_4:
        float, input_blocks_5: float, input_blocks_6: float, input_blocks_7:
        float, input_blocks_8: float, middle_block_0: float, middle_block_1:
        float, middle_block_2: float, output_blocks_0: float,
        output_blocks_1: float, output_blocks_2: float, output_blocks_3:
        float, output_blocks_4: float, output_blocks_5: float,
        output_blocks_6: float, output_blocks_7: float, output_blocks_8:
        float, out: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'time_embed.': to_comfy_input
            (time_embed), 'label_emb.': to_comfy_input(label_emb),
            'input_blocks.0': to_comfy_input(input_blocks_0),
            'input_blocks.1': to_comfy_input(input_blocks_1),
            'input_blocks.2': to_comfy_input(input_blocks_2),
            'input_blocks.3': to_comfy_input(input_blocks_3),
            'input_blocks.4': to_comfy_input(input_blocks_4),
            'input_blocks.5': to_comfy_input(input_blocks_5),
            'input_blocks.6': to_comfy_input(input_blocks_6),
            'input_blocks.7': to_comfy_input(input_blocks_7),
            'input_blocks.8': to_comfy_input(input_blocks_8),
            'middle_block.0': to_comfy_input(middle_block_0),
            'middle_block.1': to_comfy_input(middle_block_1),
            'middle_block.2': to_comfy_input(middle_block_2),
            'output_blocks.0': to_comfy_input(output_blocks_0),
            'output_blocks.1': to_comfy_input(output_blocks_1),
            'output_blocks.2': to_comfy_input(output_blocks_2),
            'output_blocks.3': to_comfy_input(output_blocks_3),
            'output_blocks.4': to_comfy_input(output_blocks_4),
            'output_blocks.5': to_comfy_input(output_blocks_5),
            'output_blocks.6': to_comfy_input(output_blocks_6),
            'output_blocks.7': to_comfy_input(output_blocks_7),
            'output_blocks.8': to_comfy_input(output_blocks_8), 'out.':
            to_comfy_input(out)}, 'class_type': 'ModelMergeSDXL'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeSD3_2B(self, model1: MODEL, model2: MODEL, pos_embed:
        float, x_embedder: float, context_embedder: float, y_embedder:
        float, t_embedder: float, joint_blocks_0: float, joint_blocks_1:
        float, joint_blocks_2: float, joint_blocks_3: float, joint_blocks_4:
        float, joint_blocks_5: float, joint_blocks_6: float, joint_blocks_7:
        float, joint_blocks_8: float, joint_blocks_9: float,
        joint_blocks_10: float, joint_blocks_11: float, joint_blocks_12:
        float, joint_blocks_13: float, joint_blocks_14: float,
        joint_blocks_15: float, joint_blocks_16: float, joint_blocks_17:
        float, joint_blocks_18: float, joint_blocks_19: float,
        joint_blocks_20: float, joint_blocks_21: float, joint_blocks_22:
        float, joint_blocks_23: float, final_layer: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'pos_embed.': to_comfy_input(
            pos_embed), 'x_embedder.': to_comfy_input(x_embedder),
            'context_embedder.': to_comfy_input(context_embedder),
            'y_embedder.': to_comfy_input(y_embedder), 't_embedder.':
            to_comfy_input(t_embedder), 'joint_blocks.0.': to_comfy_input(
            joint_blocks_0), 'joint_blocks.1.': to_comfy_input(
            joint_blocks_1), 'joint_blocks.2.': to_comfy_input(
            joint_blocks_2), 'joint_blocks.3.': to_comfy_input(
            joint_blocks_3), 'joint_blocks.4.': to_comfy_input(
            joint_blocks_4), 'joint_blocks.5.': to_comfy_input(
            joint_blocks_5), 'joint_blocks.6.': to_comfy_input(
            joint_blocks_6), 'joint_blocks.7.': to_comfy_input(
            joint_blocks_7), 'joint_blocks.8.': to_comfy_input(
            joint_blocks_8), 'joint_blocks.9.': to_comfy_input(
            joint_blocks_9), 'joint_blocks.10.': to_comfy_input(
            joint_blocks_10), 'joint_blocks.11.': to_comfy_input(
            joint_blocks_11), 'joint_blocks.12.': to_comfy_input(
            joint_blocks_12), 'joint_blocks.13.': to_comfy_input(
            joint_blocks_13), 'joint_blocks.14.': to_comfy_input(
            joint_blocks_14), 'joint_blocks.15.': to_comfy_input(
            joint_blocks_15), 'joint_blocks.16.': to_comfy_input(
            joint_blocks_16), 'joint_blocks.17.': to_comfy_input(
            joint_blocks_17), 'joint_blocks.18.': to_comfy_input(
            joint_blocks_18), 'joint_blocks.19.': to_comfy_input(
            joint_blocks_19), 'joint_blocks.20.': to_comfy_input(
            joint_blocks_20), 'joint_blocks.21.': to_comfy_input(
            joint_blocks_21), 'joint_blocks.22.': to_comfy_input(
            joint_blocks_22), 'joint_blocks.23.': to_comfy_input(
            joint_blocks_23), 'final_layer.': to_comfy_input(final_layer)},
            'class_type': 'ModelMergeSD3_2B'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeAuraflow(self, model1: MODEL, model2: MODEL,
        init_x_linear: float, positional_encoding: float, cond_seq_linear:
        float, register_tokens: float, t_embedder: float, double_layers_0:
        float, double_layers_1: float, double_layers_2: float,
        double_layers_3: float, single_layers_0: float, single_layers_1:
        float, single_layers_2: float, single_layers_3: float,
        single_layers_4: float, single_layers_5: float, single_layers_6:
        float, single_layers_7: float, single_layers_8: float,
        single_layers_9: float, single_layers_10: float, single_layers_11:
        float, single_layers_12: float, single_layers_13: float,
        single_layers_14: float, single_layers_15: float, single_layers_16:
        float, single_layers_17: float, single_layers_18: float,
        single_layers_19: float, single_layers_20: float, single_layers_21:
        float, single_layers_22: float, single_layers_23: float,
        single_layers_24: float, single_layers_25: float, single_layers_26:
        float, single_layers_27: float, single_layers_28: float,
        single_layers_29: float, single_layers_30: float, single_layers_31:
        float, modF: float, final_linear: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'init_x_linear.':
            to_comfy_input(init_x_linear), 'positional_encoding':
            to_comfy_input(positional_encoding), 'cond_seq_linear.':
            to_comfy_input(cond_seq_linear), 'register_tokens':
            to_comfy_input(register_tokens), 't_embedder.': to_comfy_input(
            t_embedder), 'double_layers.0.': to_comfy_input(double_layers_0
            ), 'double_layers.1.': to_comfy_input(double_layers_1),
            'double_layers.2.': to_comfy_input(double_layers_2),
            'double_layers.3.': to_comfy_input(double_layers_3),
            'single_layers.0.': to_comfy_input(single_layers_0),
            'single_layers.1.': to_comfy_input(single_layers_1),
            'single_layers.2.': to_comfy_input(single_layers_2),
            'single_layers.3.': to_comfy_input(single_layers_3),
            'single_layers.4.': to_comfy_input(single_layers_4),
            'single_layers.5.': to_comfy_input(single_layers_5),
            'single_layers.6.': to_comfy_input(single_layers_6),
            'single_layers.7.': to_comfy_input(single_layers_7),
            'single_layers.8.': to_comfy_input(single_layers_8),
            'single_layers.9.': to_comfy_input(single_layers_9),
            'single_layers.10.': to_comfy_input(single_layers_10),
            'single_layers.11.': to_comfy_input(single_layers_11),
            'single_layers.12.': to_comfy_input(single_layers_12),
            'single_layers.13.': to_comfy_input(single_layers_13),
            'single_layers.14.': to_comfy_input(single_layers_14),
            'single_layers.15.': to_comfy_input(single_layers_15),
            'single_layers.16.': to_comfy_input(single_layers_16),
            'single_layers.17.': to_comfy_input(single_layers_17),
            'single_layers.18.': to_comfy_input(single_layers_18),
            'single_layers.19.': to_comfy_input(single_layers_19),
            'single_layers.20.': to_comfy_input(single_layers_20),
            'single_layers.21.': to_comfy_input(single_layers_21),
            'single_layers.22.': to_comfy_input(single_layers_22),
            'single_layers.23.': to_comfy_input(single_layers_23),
            'single_layers.24.': to_comfy_input(single_layers_24),
            'single_layers.25.': to_comfy_input(single_layers_25),
            'single_layers.26.': to_comfy_input(single_layers_26),
            'single_layers.27.': to_comfy_input(single_layers_27),
            'single_layers.28.': to_comfy_input(single_layers_28),
            'single_layers.29.': to_comfy_input(single_layers_29),
            'single_layers.30.': to_comfy_input(single_layers_30),
            'single_layers.31.': to_comfy_input(single_layers_31), 'modF.':
            to_comfy_input(modF), 'final_linear.': to_comfy_input(
            final_linear)}, 'class_type': 'ModelMergeAuraflow'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeFlux1(self, model1: MODEL, model2: MODEL, img_in: float,
        time_in: float, guidance_in: float, vector_in: float, txt_in: float,
        double_blocks_0: float, double_blocks_1: float, double_blocks_2:
        float, double_blocks_3: float, double_blocks_4: float,
        double_blocks_5: float, double_blocks_6: float, double_blocks_7:
        float, double_blocks_8: float, double_blocks_9: float,
        double_blocks_10: float, double_blocks_11: float, double_blocks_12:
        float, double_blocks_13: float, double_blocks_14: float,
        double_blocks_15: float, double_blocks_16: float, double_blocks_17:
        float, double_blocks_18: float, single_blocks_0: float,
        single_blocks_1: float, single_blocks_2: float, single_blocks_3:
        float, single_blocks_4: float, single_blocks_5: float,
        single_blocks_6: float, single_blocks_7: float, single_blocks_8:
        float, single_blocks_9: float, single_blocks_10: float,
        single_blocks_11: float, single_blocks_12: float, single_blocks_13:
        float, single_blocks_14: float, single_blocks_15: float,
        single_blocks_16: float, single_blocks_17: float, single_blocks_18:
        float, single_blocks_19: float, single_blocks_20: float,
        single_blocks_21: float, single_blocks_22: float, single_blocks_23:
        float, single_blocks_24: float, single_blocks_25: float,
        single_blocks_26: float, single_blocks_27: float, single_blocks_28:
        float, single_blocks_29: float, single_blocks_30: float,
        single_blocks_31: float, single_blocks_32: float, single_blocks_33:
        float, single_blocks_34: float, single_blocks_35: float,
        single_blocks_36: float, single_blocks_37: float, final_layer: float
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'img_in.': to_comfy_input(
            img_in), 'time_in.': to_comfy_input(time_in), 'guidance_in':
            to_comfy_input(guidance_in), 'vector_in.': to_comfy_input(
            vector_in), 'txt_in.': to_comfy_input(txt_in),
            'double_blocks.0.': to_comfy_input(double_blocks_0),
            'double_blocks.1.': to_comfy_input(double_blocks_1),
            'double_blocks.2.': to_comfy_input(double_blocks_2),
            'double_blocks.3.': to_comfy_input(double_blocks_3),
            'double_blocks.4.': to_comfy_input(double_blocks_4),
            'double_blocks.5.': to_comfy_input(double_blocks_5),
            'double_blocks.6.': to_comfy_input(double_blocks_6),
            'double_blocks.7.': to_comfy_input(double_blocks_7),
            'double_blocks.8.': to_comfy_input(double_blocks_8),
            'double_blocks.9.': to_comfy_input(double_blocks_9),
            'double_blocks.10.': to_comfy_input(double_blocks_10),
            'double_blocks.11.': to_comfy_input(double_blocks_11),
            'double_blocks.12.': to_comfy_input(double_blocks_12),
            'double_blocks.13.': to_comfy_input(double_blocks_13),
            'double_blocks.14.': to_comfy_input(double_blocks_14),
            'double_blocks.15.': to_comfy_input(double_blocks_15),
            'double_blocks.16.': to_comfy_input(double_blocks_16),
            'double_blocks.17.': to_comfy_input(double_blocks_17),
            'double_blocks.18.': to_comfy_input(double_blocks_18),
            'single_blocks.0.': to_comfy_input(single_blocks_0),
            'single_blocks.1.': to_comfy_input(single_blocks_1),
            'single_blocks.2.': to_comfy_input(single_blocks_2),
            'single_blocks.3.': to_comfy_input(single_blocks_3),
            'single_blocks.4.': to_comfy_input(single_blocks_4),
            'single_blocks.5.': to_comfy_input(single_blocks_5),
            'single_blocks.6.': to_comfy_input(single_blocks_6),
            'single_blocks.7.': to_comfy_input(single_blocks_7),
            'single_blocks.8.': to_comfy_input(single_blocks_8),
            'single_blocks.9.': to_comfy_input(single_blocks_9),
            'single_blocks.10.': to_comfy_input(single_blocks_10),
            'single_blocks.11.': to_comfy_input(single_blocks_11),
            'single_blocks.12.': to_comfy_input(single_blocks_12),
            'single_blocks.13.': to_comfy_input(single_blocks_13),
            'single_blocks.14.': to_comfy_input(single_blocks_14),
            'single_blocks.15.': to_comfy_input(single_blocks_15),
            'single_blocks.16.': to_comfy_input(single_blocks_16),
            'single_blocks.17.': to_comfy_input(single_blocks_17),
            'single_blocks.18.': to_comfy_input(single_blocks_18),
            'single_blocks.19.': to_comfy_input(single_blocks_19),
            'single_blocks.20.': to_comfy_input(single_blocks_20),
            'single_blocks.21.': to_comfy_input(single_blocks_21),
            'single_blocks.22.': to_comfy_input(single_blocks_22),
            'single_blocks.23.': to_comfy_input(single_blocks_23),
            'single_blocks.24.': to_comfy_input(single_blocks_24),
            'single_blocks.25.': to_comfy_input(single_blocks_25),
            'single_blocks.26.': to_comfy_input(single_blocks_26),
            'single_blocks.27.': to_comfy_input(single_blocks_27),
            'single_blocks.28.': to_comfy_input(single_blocks_28),
            'single_blocks.29.': to_comfy_input(single_blocks_29),
            'single_blocks.30.': to_comfy_input(single_blocks_30),
            'single_blocks.31.': to_comfy_input(single_blocks_31),
            'single_blocks.32.': to_comfy_input(single_blocks_32),
            'single_blocks.33.': to_comfy_input(single_blocks_33),
            'single_blocks.34.': to_comfy_input(single_blocks_34),
            'single_blocks.35.': to_comfy_input(single_blocks_35),
            'single_blocks.36.': to_comfy_input(single_blocks_36),
            'single_blocks.37.': to_comfy_input(single_blocks_37),
            'final_layer.': to_comfy_input(final_layer)}, 'class_type':
            'ModelMergeFlux1'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeSD35_Large(self, model1: MODEL, model2: MODEL, pos_embed:
        float, x_embedder: float, context_embedder: float, y_embedder:
        float, t_embedder: float, joint_blocks_0: float, joint_blocks_1:
        float, joint_blocks_2: float, joint_blocks_3: float, joint_blocks_4:
        float, joint_blocks_5: float, joint_blocks_6: float, joint_blocks_7:
        float, joint_blocks_8: float, joint_blocks_9: float,
        joint_blocks_10: float, joint_blocks_11: float, joint_blocks_12:
        float, joint_blocks_13: float, joint_blocks_14: float,
        joint_blocks_15: float, joint_blocks_16: float, joint_blocks_17:
        float, joint_blocks_18: float, joint_blocks_19: float,
        joint_blocks_20: float, joint_blocks_21: float, joint_blocks_22:
        float, joint_blocks_23: float, joint_blocks_24: float,
        joint_blocks_25: float, joint_blocks_26: float, joint_blocks_27:
        float, joint_blocks_28: float, joint_blocks_29: float,
        joint_blocks_30: float, joint_blocks_31: float, joint_blocks_32:
        float, joint_blocks_33: float, joint_blocks_34: float,
        joint_blocks_35: float, joint_blocks_36: float, joint_blocks_37:
        float, final_layer: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'pos_embed.': to_comfy_input(
            pos_embed), 'x_embedder.': to_comfy_input(x_embedder),
            'context_embedder.': to_comfy_input(context_embedder),
            'y_embedder.': to_comfy_input(y_embedder), 't_embedder.':
            to_comfy_input(t_embedder), 'joint_blocks.0.': to_comfy_input(
            joint_blocks_0), 'joint_blocks.1.': to_comfy_input(
            joint_blocks_1), 'joint_blocks.2.': to_comfy_input(
            joint_blocks_2), 'joint_blocks.3.': to_comfy_input(
            joint_blocks_3), 'joint_blocks.4.': to_comfy_input(
            joint_blocks_4), 'joint_blocks.5.': to_comfy_input(
            joint_blocks_5), 'joint_blocks.6.': to_comfy_input(
            joint_blocks_6), 'joint_blocks.7.': to_comfy_input(
            joint_blocks_7), 'joint_blocks.8.': to_comfy_input(
            joint_blocks_8), 'joint_blocks.9.': to_comfy_input(
            joint_blocks_9), 'joint_blocks.10.': to_comfy_input(
            joint_blocks_10), 'joint_blocks.11.': to_comfy_input(
            joint_blocks_11), 'joint_blocks.12.': to_comfy_input(
            joint_blocks_12), 'joint_blocks.13.': to_comfy_input(
            joint_blocks_13), 'joint_blocks.14.': to_comfy_input(
            joint_blocks_14), 'joint_blocks.15.': to_comfy_input(
            joint_blocks_15), 'joint_blocks.16.': to_comfy_input(
            joint_blocks_16), 'joint_blocks.17.': to_comfy_input(
            joint_blocks_17), 'joint_blocks.18.': to_comfy_input(
            joint_blocks_18), 'joint_blocks.19.': to_comfy_input(
            joint_blocks_19), 'joint_blocks.20.': to_comfy_input(
            joint_blocks_20), 'joint_blocks.21.': to_comfy_input(
            joint_blocks_21), 'joint_blocks.22.': to_comfy_input(
            joint_blocks_22), 'joint_blocks.23.': to_comfy_input(
            joint_blocks_23), 'joint_blocks.24.': to_comfy_input(
            joint_blocks_24), 'joint_blocks.25.': to_comfy_input(
            joint_blocks_25), 'joint_blocks.26.': to_comfy_input(
            joint_blocks_26), 'joint_blocks.27.': to_comfy_input(
            joint_blocks_27), 'joint_blocks.28.': to_comfy_input(
            joint_blocks_28), 'joint_blocks.29.': to_comfy_input(
            joint_blocks_29), 'joint_blocks.30.': to_comfy_input(
            joint_blocks_30), 'joint_blocks.31.': to_comfy_input(
            joint_blocks_31), 'joint_blocks.32.': to_comfy_input(
            joint_blocks_32), 'joint_blocks.33.': to_comfy_input(
            joint_blocks_33), 'joint_blocks.34.': to_comfy_input(
            joint_blocks_34), 'joint_blocks.35.': to_comfy_input(
            joint_blocks_35), 'joint_blocks.36.': to_comfy_input(
            joint_blocks_36), 'joint_blocks.37.': to_comfy_input(
            joint_blocks_37), 'final_layer.': to_comfy_input(final_layer)},
            'class_type': 'ModelMergeSD35_Large'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeMochiPreview(self, model1: MODEL, model2: MODEL,
        pos_frequencies: float, t_embedder: float, t5_y_embedder: float,
        t5_yproj: float, blocks_0: float, blocks_1: float, blocks_2: float,
        blocks_3: float, blocks_4: float, blocks_5: float, blocks_6: float,
        blocks_7: float, blocks_8: float, blocks_9: float, blocks_10: float,
        blocks_11: float, blocks_12: float, blocks_13: float, blocks_14:
        float, blocks_15: float, blocks_16: float, blocks_17: float,
        blocks_18: float, blocks_19: float, blocks_20: float, blocks_21:
        float, blocks_22: float, blocks_23: float, blocks_24: float,
        blocks_25: float, blocks_26: float, blocks_27: float, blocks_28:
        float, blocks_29: float, blocks_30: float, blocks_31: float,
        blocks_32: float, blocks_33: float, blocks_34: float, blocks_35:
        float, blocks_36: float, blocks_37: float, blocks_38: float,
        blocks_39: float, blocks_40: float, blocks_41: float, blocks_42:
        float, blocks_43: float, blocks_44: float, blocks_45: float,
        blocks_46: float, blocks_47: float, final_layer: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'pos_frequencies.':
            to_comfy_input(pos_frequencies), 't_embedder.': to_comfy_input(
            t_embedder), 't5_y_embedder.': to_comfy_input(t5_y_embedder),
            't5_yproj.': to_comfy_input(t5_yproj), 'blocks.0.':
            to_comfy_input(blocks_0), 'blocks.1.': to_comfy_input(blocks_1),
            'blocks.2.': to_comfy_input(blocks_2), 'blocks.3.':
            to_comfy_input(blocks_3), 'blocks.4.': to_comfy_input(blocks_4),
            'blocks.5.': to_comfy_input(blocks_5), 'blocks.6.':
            to_comfy_input(blocks_6), 'blocks.7.': to_comfy_input(blocks_7),
            'blocks.8.': to_comfy_input(blocks_8), 'blocks.9.':
            to_comfy_input(blocks_9), 'blocks.10.': to_comfy_input(
            blocks_10), 'blocks.11.': to_comfy_input(blocks_11),
            'blocks.12.': to_comfy_input(blocks_12), 'blocks.13.':
            to_comfy_input(blocks_13), 'blocks.14.': to_comfy_input(
            blocks_14), 'blocks.15.': to_comfy_input(blocks_15),
            'blocks.16.': to_comfy_input(blocks_16), 'blocks.17.':
            to_comfy_input(blocks_17), 'blocks.18.': to_comfy_input(
            blocks_18), 'blocks.19.': to_comfy_input(blocks_19),
            'blocks.20.': to_comfy_input(blocks_20), 'blocks.21.':
            to_comfy_input(blocks_21), 'blocks.22.': to_comfy_input(
            blocks_22), 'blocks.23.': to_comfy_input(blocks_23),
            'blocks.24.': to_comfy_input(blocks_24), 'blocks.25.':
            to_comfy_input(blocks_25), 'blocks.26.': to_comfy_input(
            blocks_26), 'blocks.27.': to_comfy_input(blocks_27),
            'blocks.28.': to_comfy_input(blocks_28), 'blocks.29.':
            to_comfy_input(blocks_29), 'blocks.30.': to_comfy_input(
            blocks_30), 'blocks.31.': to_comfy_input(blocks_31),
            'blocks.32.': to_comfy_input(blocks_32), 'blocks.33.':
            to_comfy_input(blocks_33), 'blocks.34.': to_comfy_input(
            blocks_34), 'blocks.35.': to_comfy_input(blocks_35),
            'blocks.36.': to_comfy_input(blocks_36), 'blocks.37.':
            to_comfy_input(blocks_37), 'blocks.38.': to_comfy_input(
            blocks_38), 'blocks.39.': to_comfy_input(blocks_39),
            'blocks.40.': to_comfy_input(blocks_40), 'blocks.41.':
            to_comfy_input(blocks_41), 'blocks.42.': to_comfy_input(
            blocks_42), 'blocks.43.': to_comfy_input(blocks_43),
            'blocks.44.': to_comfy_input(blocks_44), 'blocks.45.':
            to_comfy_input(blocks_45), 'blocks.46.': to_comfy_input(
            blocks_46), 'blocks.47.': to_comfy_input(blocks_47),
            'final_layer.': to_comfy_input(final_layer)}, 'class_type':
            'ModelMergeMochiPreview'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeLTXV(self, model1: MODEL, model2: MODEL, patchify_proj:
        float, adaln_single: float, caption_projection: float,
        transformer_blocks_0: float, transformer_blocks_1: float,
        transformer_blocks_2: float, transformer_blocks_3: float,
        transformer_blocks_4: float, transformer_blocks_5: float,
        transformer_blocks_6: float, transformer_blocks_7: float,
        transformer_blocks_8: float, transformer_blocks_9: float,
        transformer_blocks_10: float, transformer_blocks_11: float,
        transformer_blocks_12: float, transformer_blocks_13: float,
        transformer_blocks_14: float, transformer_blocks_15: float,
        transformer_blocks_16: float, transformer_blocks_17: float,
        transformer_blocks_18: float, transformer_blocks_19: float,
        transformer_blocks_20: float, transformer_blocks_21: float,
        transformer_blocks_22: float, transformer_blocks_23: float,
        transformer_blocks_24: float, transformer_blocks_25: float,
        transformer_blocks_26: float, transformer_blocks_27: float,
        scale_shift_table: float, proj_out: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'patchify_proj.':
            to_comfy_input(patchify_proj), 'adaln_single.': to_comfy_input(
            adaln_single), 'caption_projection.': to_comfy_input(
            caption_projection), 'transformer_blocks.0.': to_comfy_input(
            transformer_blocks_0), 'transformer_blocks.1.': to_comfy_input(
            transformer_blocks_1), 'transformer_blocks.2.': to_comfy_input(
            transformer_blocks_2), 'transformer_blocks.3.': to_comfy_input(
            transformer_blocks_3), 'transformer_blocks.4.': to_comfy_input(
            transformer_blocks_4), 'transformer_blocks.5.': to_comfy_input(
            transformer_blocks_5), 'transformer_blocks.6.': to_comfy_input(
            transformer_blocks_6), 'transformer_blocks.7.': to_comfy_input(
            transformer_blocks_7), 'transformer_blocks.8.': to_comfy_input(
            transformer_blocks_8), 'transformer_blocks.9.': to_comfy_input(
            transformer_blocks_9), 'transformer_blocks.10.': to_comfy_input
            (transformer_blocks_10), 'transformer_blocks.11.':
            to_comfy_input(transformer_blocks_11), 'transformer_blocks.12.':
            to_comfy_input(transformer_blocks_12), 'transformer_blocks.13.':
            to_comfy_input(transformer_blocks_13), 'transformer_blocks.14.':
            to_comfy_input(transformer_blocks_14), 'transformer_blocks.15.':
            to_comfy_input(transformer_blocks_15), 'transformer_blocks.16.':
            to_comfy_input(transformer_blocks_16), 'transformer_blocks.17.':
            to_comfy_input(transformer_blocks_17), 'transformer_blocks.18.':
            to_comfy_input(transformer_blocks_18), 'transformer_blocks.19.':
            to_comfy_input(transformer_blocks_19), 'transformer_blocks.20.':
            to_comfy_input(transformer_blocks_20), 'transformer_blocks.21.':
            to_comfy_input(transformer_blocks_21), 'transformer_blocks.22.':
            to_comfy_input(transformer_blocks_22), 'transformer_blocks.23.':
            to_comfy_input(transformer_blocks_23), 'transformer_blocks.24.':
            to_comfy_input(transformer_blocks_24), 'transformer_blocks.25.':
            to_comfy_input(transformer_blocks_25), 'transformer_blocks.26.':
            to_comfy_input(transformer_blocks_26), 'transformer_blocks.27.':
            to_comfy_input(transformer_blocks_27), 'scale_shift_table':
            to_comfy_input(scale_shift_table), 'proj_out.': to_comfy_input(
            proj_out)}, 'class_type': 'ModelMergeLTXV'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeCosmos7B(self, model1: MODEL, model2: MODEL, pos_embedder:
        float, extra_pos_embedder: float, x_embedder: float, t_embedder:
        float, affline_norm: float, blocks_block0: float, blocks_block1:
        float, blocks_block2: float, blocks_block3: float, blocks_block4:
        float, blocks_block5: float, blocks_block6: float, blocks_block7:
        float, blocks_block8: float, blocks_block9: float, blocks_block10:
        float, blocks_block11: float, blocks_block12: float, blocks_block13:
        float, blocks_block14: float, blocks_block15: float, blocks_block16:
        float, blocks_block17: float, blocks_block18: float, blocks_block19:
        float, blocks_block20: float, blocks_block21: float, blocks_block22:
        float, blocks_block23: float, blocks_block24: float, blocks_block25:
        float, blocks_block26: float, blocks_block27: float, final_layer: float
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'pos_embedder.':
            to_comfy_input(pos_embedder), 'extra_pos_embedder.':
            to_comfy_input(extra_pos_embedder), 'x_embedder.':
            to_comfy_input(x_embedder), 't_embedder.': to_comfy_input(
            t_embedder), 'affline_norm.': to_comfy_input(affline_norm),
            'blocks.block0.': to_comfy_input(blocks_block0),
            'blocks.block1.': to_comfy_input(blocks_block1),
            'blocks.block2.': to_comfy_input(blocks_block2),
            'blocks.block3.': to_comfy_input(blocks_block3),
            'blocks.block4.': to_comfy_input(blocks_block4),
            'blocks.block5.': to_comfy_input(blocks_block5),
            'blocks.block6.': to_comfy_input(blocks_block6),
            'blocks.block7.': to_comfy_input(blocks_block7),
            'blocks.block8.': to_comfy_input(blocks_block8),
            'blocks.block9.': to_comfy_input(blocks_block9),
            'blocks.block10.': to_comfy_input(blocks_block10),
            'blocks.block11.': to_comfy_input(blocks_block11),
            'blocks.block12.': to_comfy_input(blocks_block12),
            'blocks.block13.': to_comfy_input(blocks_block13),
            'blocks.block14.': to_comfy_input(blocks_block14),
            'blocks.block15.': to_comfy_input(blocks_block15),
            'blocks.block16.': to_comfy_input(blocks_block16),
            'blocks.block17.': to_comfy_input(blocks_block17),
            'blocks.block18.': to_comfy_input(blocks_block18),
            'blocks.block19.': to_comfy_input(blocks_block19),
            'blocks.block20.': to_comfy_input(blocks_block20),
            'blocks.block21.': to_comfy_input(blocks_block21),
            'blocks.block22.': to_comfy_input(blocks_block22),
            'blocks.block23.': to_comfy_input(blocks_block23),
            'blocks.block24.': to_comfy_input(blocks_block24),
            'blocks.block25.': to_comfy_input(blocks_block25),
            'blocks.block26.': to_comfy_input(blocks_block26),
            'blocks.block27.': to_comfy_input(blocks_block27),
            'final_layer.': to_comfy_input(final_layer)}, 'class_type':
            'ModelMergeCosmos7B'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeCosmos14B(self, model1: MODEL, model2: MODEL,
        pos_embedder: float, extra_pos_embedder: float, x_embedder: float,
        t_embedder: float, affline_norm: float, blocks_block0: float,
        blocks_block1: float, blocks_block2: float, blocks_block3: float,
        blocks_block4: float, blocks_block5: float, blocks_block6: float,
        blocks_block7: float, blocks_block8: float, blocks_block9: float,
        blocks_block10: float, blocks_block11: float, blocks_block12: float,
        blocks_block13: float, blocks_block14: float, blocks_block15: float,
        blocks_block16: float, blocks_block17: float, blocks_block18: float,
        blocks_block19: float, blocks_block20: float, blocks_block21: float,
        blocks_block22: float, blocks_block23: float, blocks_block24: float,
        blocks_block25: float, blocks_block26: float, blocks_block27: float,
        blocks_block28: float, blocks_block29: float, blocks_block30: float,
        blocks_block31: float, blocks_block32: float, blocks_block33: float,
        blocks_block34: float, blocks_block35: float, final_layer: float
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'pos_embedder.':
            to_comfy_input(pos_embedder), 'extra_pos_embedder.':
            to_comfy_input(extra_pos_embedder), 'x_embedder.':
            to_comfy_input(x_embedder), 't_embedder.': to_comfy_input(
            t_embedder), 'affline_norm.': to_comfy_input(affline_norm),
            'blocks.block0.': to_comfy_input(blocks_block0),
            'blocks.block1.': to_comfy_input(blocks_block1),
            'blocks.block2.': to_comfy_input(blocks_block2),
            'blocks.block3.': to_comfy_input(blocks_block3),
            'blocks.block4.': to_comfy_input(blocks_block4),
            'blocks.block5.': to_comfy_input(blocks_block5),
            'blocks.block6.': to_comfy_input(blocks_block6),
            'blocks.block7.': to_comfy_input(blocks_block7),
            'blocks.block8.': to_comfy_input(blocks_block8),
            'blocks.block9.': to_comfy_input(blocks_block9),
            'blocks.block10.': to_comfy_input(blocks_block10),
            'blocks.block11.': to_comfy_input(blocks_block11),
            'blocks.block12.': to_comfy_input(blocks_block12),
            'blocks.block13.': to_comfy_input(blocks_block13),
            'blocks.block14.': to_comfy_input(blocks_block14),
            'blocks.block15.': to_comfy_input(blocks_block15),
            'blocks.block16.': to_comfy_input(blocks_block16),
            'blocks.block17.': to_comfy_input(blocks_block17),
            'blocks.block18.': to_comfy_input(blocks_block18),
            'blocks.block19.': to_comfy_input(blocks_block19),
            'blocks.block20.': to_comfy_input(blocks_block20),
            'blocks.block21.': to_comfy_input(blocks_block21),
            'blocks.block22.': to_comfy_input(blocks_block22),
            'blocks.block23.': to_comfy_input(blocks_block23),
            'blocks.block24.': to_comfy_input(blocks_block24),
            'blocks.block25.': to_comfy_input(blocks_block25),
            'blocks.block26.': to_comfy_input(blocks_block26),
            'blocks.block27.': to_comfy_input(blocks_block27),
            'blocks.block28.': to_comfy_input(blocks_block28),
            'blocks.block29.': to_comfy_input(blocks_block29),
            'blocks.block30.': to_comfy_input(blocks_block30),
            'blocks.block31.': to_comfy_input(blocks_block31),
            'blocks.block32.': to_comfy_input(blocks_block32),
            'blocks.block33.': to_comfy_input(blocks_block33),
            'blocks.block34.': to_comfy_input(blocks_block34),
            'blocks.block35.': to_comfy_input(blocks_block35),
            'final_layer.': to_comfy_input(final_layer)}, 'class_type':
            'ModelMergeCosmos14B'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeWAN2_1(self, model1: MODEL, model2: MODEL,
        patch_embedding: float, time_embedding: float, time_projection:
        float, text_embedding: float, img_emb: float, blocks_0: float,
        blocks_1: float, blocks_2: float, blocks_3: float, blocks_4: float,
        blocks_5: float, blocks_6: float, blocks_7: float, blocks_8: float,
        blocks_9: float, blocks_10: float, blocks_11: float, blocks_12:
        float, blocks_13: float, blocks_14: float, blocks_15: float,
        blocks_16: float, blocks_17: float, blocks_18: float, blocks_19:
        float, blocks_20: float, blocks_21: float, blocks_22: float,
        blocks_23: float, blocks_24: float, blocks_25: float, blocks_26:
        float, blocks_27: float, blocks_28: float, blocks_29: float,
        blocks_30: float, blocks_31: float, blocks_32: float, blocks_33:
        float, blocks_34: float, blocks_35: float, blocks_36: float,
        blocks_37: float, blocks_38: float, blocks_39: float, head: float
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'patch_embedding.':
            to_comfy_input(patch_embedding), 'time_embedding.':
            to_comfy_input(time_embedding), 'time_projection.':
            to_comfy_input(time_projection), 'text_embedding.':
            to_comfy_input(text_embedding), 'img_emb.': to_comfy_input(
            img_emb), 'blocks.0.': to_comfy_input(blocks_0), 'blocks.1.':
            to_comfy_input(blocks_1), 'blocks.2.': to_comfy_input(blocks_2),
            'blocks.3.': to_comfy_input(blocks_3), 'blocks.4.':
            to_comfy_input(blocks_4), 'blocks.5.': to_comfy_input(blocks_5),
            'blocks.6.': to_comfy_input(blocks_6), 'blocks.7.':
            to_comfy_input(blocks_7), 'blocks.8.': to_comfy_input(blocks_8),
            'blocks.9.': to_comfy_input(blocks_9), 'blocks.10.':
            to_comfy_input(blocks_10), 'blocks.11.': to_comfy_input(
            blocks_11), 'blocks.12.': to_comfy_input(blocks_12),
            'blocks.13.': to_comfy_input(blocks_13), 'blocks.14.':
            to_comfy_input(blocks_14), 'blocks.15.': to_comfy_input(
            blocks_15), 'blocks.16.': to_comfy_input(blocks_16),
            'blocks.17.': to_comfy_input(blocks_17), 'blocks.18.':
            to_comfy_input(blocks_18), 'blocks.19.': to_comfy_input(
            blocks_19), 'blocks.20.': to_comfy_input(blocks_20),
            'blocks.21.': to_comfy_input(blocks_21), 'blocks.22.':
            to_comfy_input(blocks_22), 'blocks.23.': to_comfy_input(
            blocks_23), 'blocks.24.': to_comfy_input(blocks_24),
            'blocks.25.': to_comfy_input(blocks_25), 'blocks.26.':
            to_comfy_input(blocks_26), 'blocks.27.': to_comfy_input(
            blocks_27), 'blocks.28.': to_comfy_input(blocks_28),
            'blocks.29.': to_comfy_input(blocks_29), 'blocks.30.':
            to_comfy_input(blocks_30), 'blocks.31.': to_comfy_input(
            blocks_31), 'blocks.32.': to_comfy_input(blocks_32),
            'blocks.33.': to_comfy_input(blocks_33), 'blocks.34.':
            to_comfy_input(blocks_34), 'blocks.35.': to_comfy_input(
            blocks_35), 'blocks.36.': to_comfy_input(blocks_36),
            'blocks.37.': to_comfy_input(blocks_37), 'blocks.38.':
            to_comfy_input(blocks_38), 'blocks.39.': to_comfy_input(
            blocks_39), 'head.': to_comfy_input(head)}, 'class_type':
            'ModelMergeWAN2_1'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeCosmosPredict2_2B(self, model1: MODEL, model2: MODEL,
        pos_embedder: float, x_embedder: float, t_embedder: float,
        t_embedding_norm: float, blocks_0: float, blocks_1: float, blocks_2:
        float, blocks_3: float, blocks_4: float, blocks_5: float, blocks_6:
        float, blocks_7: float, blocks_8: float, blocks_9: float, blocks_10:
        float, blocks_11: float, blocks_12: float, blocks_13: float,
        blocks_14: float, blocks_15: float, blocks_16: float, blocks_17:
        float, blocks_18: float, blocks_19: float, blocks_20: float,
        blocks_21: float, blocks_22: float, blocks_23: float, blocks_24:
        float, blocks_25: float, blocks_26: float, blocks_27: float,
        final_layer: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'pos_embedder.':
            to_comfy_input(pos_embedder), 'x_embedder.': to_comfy_input(
            x_embedder), 't_embedder.': to_comfy_input(t_embedder),
            't_embedding_norm.': to_comfy_input(t_embedding_norm),
            'blocks.0.': to_comfy_input(blocks_0), 'blocks.1.':
            to_comfy_input(blocks_1), 'blocks.2.': to_comfy_input(blocks_2),
            'blocks.3.': to_comfy_input(blocks_3), 'blocks.4.':
            to_comfy_input(blocks_4), 'blocks.5.': to_comfy_input(blocks_5),
            'blocks.6.': to_comfy_input(blocks_6), 'blocks.7.':
            to_comfy_input(blocks_7), 'blocks.8.': to_comfy_input(blocks_8),
            'blocks.9.': to_comfy_input(blocks_9), 'blocks.10.':
            to_comfy_input(blocks_10), 'blocks.11.': to_comfy_input(
            blocks_11), 'blocks.12.': to_comfy_input(blocks_12),
            'blocks.13.': to_comfy_input(blocks_13), 'blocks.14.':
            to_comfy_input(blocks_14), 'blocks.15.': to_comfy_input(
            blocks_15), 'blocks.16.': to_comfy_input(blocks_16),
            'blocks.17.': to_comfy_input(blocks_17), 'blocks.18.':
            to_comfy_input(blocks_18), 'blocks.19.': to_comfy_input(
            blocks_19), 'blocks.20.': to_comfy_input(blocks_20),
            'blocks.21.': to_comfy_input(blocks_21), 'blocks.22.':
            to_comfy_input(blocks_22), 'blocks.23.': to_comfy_input(
            blocks_23), 'blocks.24.': to_comfy_input(blocks_24),
            'blocks.25.': to_comfy_input(blocks_25), 'blocks.26.':
            to_comfy_input(blocks_26), 'blocks.27.': to_comfy_input(
            blocks_27), 'final_layer.': to_comfy_input(final_layer)},
            'class_type': 'ModelMergeCosmosPredict2_2B'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def ModelMergeCosmosPredict2_14B(self, model1: MODEL, model2: MODEL,
        pos_embedder: float, x_embedder: float, t_embedder: float,
        t_embedding_norm: float, blocks_0: float, blocks_1: float, blocks_2:
        float, blocks_3: float, blocks_4: float, blocks_5: float, blocks_6:
        float, blocks_7: float, blocks_8: float, blocks_9: float, blocks_10:
        float, blocks_11: float, blocks_12: float, blocks_13: float,
        blocks_14: float, blocks_15: float, blocks_16: float, blocks_17:
        float, blocks_18: float, blocks_19: float, blocks_20: float,
        blocks_21: float, blocks_22: float, blocks_23: float, blocks_24:
        float, blocks_25: float, blocks_26: float, blocks_27: float,
        blocks_28: float, blocks_29: float, blocks_30: float, blocks_31:
        float, blocks_32: float, blocks_33: float, blocks_34: float,
        blocks_35: float, final_layer: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model1': to_comfy_input(model1),
            'model2': to_comfy_input(model2), 'pos_embedder.':
            to_comfy_input(pos_embedder), 'x_embedder.': to_comfy_input(
            x_embedder), 't_embedder.': to_comfy_input(t_embedder),
            't_embedding_norm.': to_comfy_input(t_embedding_norm),
            'blocks.0.': to_comfy_input(blocks_0), 'blocks.1.':
            to_comfy_input(blocks_1), 'blocks.2.': to_comfy_input(blocks_2),
            'blocks.3.': to_comfy_input(blocks_3), 'blocks.4.':
            to_comfy_input(blocks_4), 'blocks.5.': to_comfy_input(blocks_5),
            'blocks.6.': to_comfy_input(blocks_6), 'blocks.7.':
            to_comfy_input(blocks_7), 'blocks.8.': to_comfy_input(blocks_8),
            'blocks.9.': to_comfy_input(blocks_9), 'blocks.10.':
            to_comfy_input(blocks_10), 'blocks.11.': to_comfy_input(
            blocks_11), 'blocks.12.': to_comfy_input(blocks_12),
            'blocks.13.': to_comfy_input(blocks_13), 'blocks.14.':
            to_comfy_input(blocks_14), 'blocks.15.': to_comfy_input(
            blocks_15), 'blocks.16.': to_comfy_input(blocks_16),
            'blocks.17.': to_comfy_input(blocks_17), 'blocks.18.':
            to_comfy_input(blocks_18), 'blocks.19.': to_comfy_input(
            blocks_19), 'blocks.20.': to_comfy_input(blocks_20),
            'blocks.21.': to_comfy_input(blocks_21), 'blocks.22.':
            to_comfy_input(blocks_22), 'blocks.23.': to_comfy_input(
            blocks_23), 'blocks.24.': to_comfy_input(blocks_24),
            'blocks.25.': to_comfy_input(blocks_25), 'blocks.26.':
            to_comfy_input(blocks_26), 'blocks.27.': to_comfy_input(
            blocks_27), 'blocks.28.': to_comfy_input(blocks_28),
            'blocks.29.': to_comfy_input(blocks_29), 'blocks.30.':
            to_comfy_input(blocks_30), 'blocks.31.': to_comfy_input(
            blocks_31), 'blocks.32.': to_comfy_input(blocks_32),
            'blocks.33.': to_comfy_input(blocks_33), 'blocks.34.':
            to_comfy_input(blocks_34), 'blocks.35.': to_comfy_input(
            blocks_35), 'final_layer.': to_comfy_input(final_layer)},
            'class_type': 'ModelMergeCosmosPredict2_14B'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def PerturbedAttentionGuidance(self, model: MODEL, scale: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'scale': to_comfy_input(scale)}, 'class_type':
            'PerturbedAttentionGuidance'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def AlignYourStepsScheduler(self, model_type: str, steps: int, denoise:
        float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_type': to_comfy_input(
            model_type), 'steps': to_comfy_input(steps), 'denoise':
            to_comfy_input(denoise)}, 'class_type': 'AlignYourStepsScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def UNetSelfAttentionMultiply(self, model: MODEL, q: float, k: float, v:
        float, out: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model), 'q':
            to_comfy_input(q), 'k': to_comfy_input(k), 'v': to_comfy_input(
            v), 'out': to_comfy_input(out)}, 'class_type':
            'UNetSelfAttentionMultiply'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def UNetCrossAttentionMultiply(self, model: MODEL, q: float, k: float,
        v: float, out: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model), 'q':
            to_comfy_input(q), 'k': to_comfy_input(k), 'v': to_comfy_input(
            v), 'out': to_comfy_input(out)}, 'class_type':
            'UNetCrossAttentionMultiply'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def CLIPAttentionMultiply(self, clip: CLIP, q: float, k: float, v:
        float, out: float) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip), 'q':
            to_comfy_input(q), 'k': to_comfy_input(k), 'v': to_comfy_input(
            v), 'out': to_comfy_input(out)}, 'class_type':
            'CLIPAttentionMultiply'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def UNetTemporalAttentionMultiply(self, model: MODEL, self_structural:
        float, self_temporal: float, cross_structural: float,
        cross_temporal: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'self_structural': to_comfy_input(self_structural),
            'self_temporal': to_comfy_input(self_temporal),
            'cross_structural': to_comfy_input(cross_structural),
            'cross_temporal': to_comfy_input(cross_temporal)}, 'class_type':
            'UNetTemporalAttentionMultiply'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def SamplerLCMUpscale(self, scale_ratio: float, scale_steps: int,
        upscale_method: str) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'scale_ratio': to_comfy_input(
            scale_ratio), 'scale_steps': to_comfy_input(scale_steps),
            'upscale_method': to_comfy_input(upscale_method)}, 'class_type':
            'SamplerLCMUpscale'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def SamplerEulerCFGpp(self, version: str) ->SAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'version': to_comfy_input(version)},
            'class_type': 'SamplerEulerCFGpp'}
        self._add_node(node_id, comfy_json_node)
        return SAMPLER(node_id, 0)

    def WebcamCapture(self, image: WEBCAM, width: int, height: int,
        capture_on_queue: bool) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'width': to_comfy_input(width), 'height': to_comfy_input(height
            ), 'capture_on_queue': to_comfy_input(capture_on_queue)},
            'class_type': 'WebcamCapture'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def EmptyLatentAudio(self, seconds: float, batch_size: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seconds': to_comfy_input(seconds),
            'batch_size': to_comfy_input(batch_size)}, 'class_type':
            'EmptyLatentAudio'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def VAEEncodeAudio(self, audio: AUDIO, vae: VAE) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'audio': to_comfy_input(audio), 'vae':
            to_comfy_input(vae)}, 'class_type': 'VAEEncodeAudio'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def VAEDecodeAudio(self, samples: LATENT, vae: VAE) ->AUDIO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'vae': to_comfy_input(vae)}, 'class_type': 'VAEDecodeAudio'}
        self._add_node(node_id, comfy_json_node)
        return AUDIO(node_id, 0)

    def SaveAudio(self, audio: AUDIO, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'audio': to_comfy_input(audio),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'SaveAudio'}
        self._add_node(node_id, comfy_json_node)

    def SaveAudioMP3(self, audio: AUDIO, filename_prefix: str, quality: str
        ) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'audio': to_comfy_input(audio),
            'filename_prefix': to_comfy_input(filename_prefix), 'quality':
            to_comfy_input(quality)}, 'class_type': 'SaveAudioMP3'}
        self._add_node(node_id, comfy_json_node)

    def SaveAudioOpus(self, audio: AUDIO, filename_prefix: str, quality: str
        ) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'audio': to_comfy_input(audio),
            'filename_prefix': to_comfy_input(filename_prefix), 'quality':
            to_comfy_input(quality)}, 'class_type': 'SaveAudioOpus'}
        self._add_node(node_id, comfy_json_node)

    def LoadAudio(self, audio: str) ->AUDIO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'audio': to_comfy_input(audio)},
            'class_type': 'LoadAudio'}
        self._add_node(node_id, comfy_json_node)
        return AUDIO(node_id, 0)

    def PreviewAudio(self, audio: AUDIO) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'audio': to_comfy_input(audio)},
            'class_type': 'PreviewAudio'}
        self._add_node(node_id, comfy_json_node)

    def ConditioningStableAudio(self, positive: CONDITIONING, negative:
        CONDITIONING, seconds_start: float, seconds_total: float) ->(
        CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'seconds_start':
            to_comfy_input(seconds_start), 'seconds_total': to_comfy_input(
            seconds_total)}, 'class_type': 'ConditioningStableAudio'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def TripleCLIPLoader(self, clip_name1: str, clip_name2: str, clip_name3:
        str) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_name1': to_comfy_input(
            clip_name1), 'clip_name2': to_comfy_input(clip_name2),
            'clip_name3': to_comfy_input(clip_name3)}, 'class_type':
            'TripleCLIPLoader'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def EmptySD3LatentImage(self, width: int, height: int, batch_size: int
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'batch_size': to_comfy_input(
            batch_size)}, 'class_type': 'EmptySD3LatentImage'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def CLIPTextEncodeSD3(self, clip: CLIP, clip_l: str, clip_g: str, t5xxl:
        str, empty_padding: str) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'clip_l': to_comfy_input(clip_l), 'clip_g': to_comfy_input(
            clip_g), 't5xxl': to_comfy_input(t5xxl), 'empty_padding':
            to_comfy_input(empty_padding)}, 'class_type': 'CLIPTextEncodeSD3'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ControlNetApplySD3(self, positive: CONDITIONING, negative:
        CONDITIONING, control_net: CONTROL_NET, vae: VAE, image: IMAGE,
        strength: float, start_percent: float, end_percent: float) ->(
        CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'control_net':
            to_comfy_input(control_net), 'vae': to_comfy_input(vae),
            'image': to_comfy_input(image), 'strength': to_comfy_input(
            strength), 'start_percent': to_comfy_input(start_percent),
            'end_percent': to_comfy_input(end_percent)}, 'class_type':
            'ControlNetApplySD3'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def SkipLayerGuidanceSD3(self, model: MODEL, layers: str, scale: float,
        start_percent: float, end_percent: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'layers': to_comfy_input(layers), 'scale': to_comfy_input(scale
            ), 'start_percent': to_comfy_input(start_percent),
            'end_percent': to_comfy_input(end_percent)}, 'class_type':
            'SkipLayerGuidanceSD3'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def GITSScheduler(self, coeff: float, steps: int, denoise: float) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'coeff': to_comfy_input(coeff),
            'steps': to_comfy_input(steps), 'denoise': to_comfy_input(
            denoise)}, 'class_type': 'GITSScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def SetUnionControlNetType(self, control_net: CONTROL_NET, type: str
        ) ->CONTROL_NET:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'control_net': to_comfy_input(
            control_net), 'type': to_comfy_input(type)}, 'class_type':
            'SetUnionControlNetType'}
        self._add_node(node_id, comfy_json_node)
        return CONTROL_NET(node_id, 0)

    def ControlNetInpaintingAliMamaApply(self, positive: CONDITIONING,
        negative: CONDITIONING, control_net: CONTROL_NET, vae: VAE, image:
        IMAGE, mask: MASK, strength: float, start_percent: float,
        end_percent: float) ->(CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'control_net':
            to_comfy_input(control_net), 'vae': to_comfy_input(vae),
            'image': to_comfy_input(image), 'mask': to_comfy_input(mask),
            'strength': to_comfy_input(strength), 'start_percent':
            to_comfy_input(start_percent), 'end_percent': to_comfy_input(
            end_percent)}, 'class_type': 'ControlNetInpaintingAliMamaApply'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def CLIPTextEncodeHunyuanDiT(self, clip: CLIP, bert: str, mt5xl: str
        ) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip), 'bert':
            to_comfy_input(bert), 'mt5xl': to_comfy_input(mt5xl)},
            'class_type': 'CLIPTextEncodeHunyuanDiT'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def TextEncodeHunyuanVideo_ImageToVideo(self, clip: CLIP,
        clip_vision_output: CLIP_VISION_OUTPUT, prompt: str,
        image_interleave: int) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'clip_vision_output': to_comfy_input(clip_vision_output),
            'prompt': to_comfy_input(prompt), 'image_interleave':
            to_comfy_input(image_interleave)}, 'class_type':
            'TextEncodeHunyuanVideo_ImageToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def EmptyHunyuanLatentVideo(self, width: int, height: int, length: int,
        batch_size: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'length': to_comfy_input(
            length), 'batch_size': to_comfy_input(batch_size)},
            'class_type': 'EmptyHunyuanLatentVideo'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def HunyuanImageToVideo(self, positive: CONDITIONING, vae: VAE, width:
        int, height: int, length: int, batch_size: int, guidance_type: str,
        start_image: IMAGE) ->(CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'vae': to_comfy_input(vae), 'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'length': to_comfy_input(
            length), 'batch_size': to_comfy_input(batch_size),
            'guidance_type': to_comfy_input(guidance_type), 'start_image':
            to_comfy_input(start_image)}, 'class_type': 'HunyuanImageToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), LATENT(node_id, 1)

    def CLIPTextEncodeFlux(self, clip: CLIP, clip_l: str, t5xxl: str,
        guidance: float) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'clip_l': to_comfy_input(clip_l), 't5xxl': to_comfy_input(t5xxl
            ), 'guidance': to_comfy_input(guidance)}, 'class_type':
            'CLIPTextEncodeFlux'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def FluxGuidance(self, conditioning: CONDITIONING, guidance: float
        ) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'guidance': to_comfy_input(guidance)},
            'class_type': 'FluxGuidance'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def FluxDisableGuidance(self, conditioning: CONDITIONING) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning)}, 'class_type': 'FluxDisableGuidance'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def FluxKontextImageScale(self, image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'FluxKontextImageScale'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LoraSave(self, filename_prefix: str, rank: int, lora_type: str,
        bias_diff: bool, model_diff: MODEL, text_encoder_diff: CLIP) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'filename_prefix': to_comfy_input(
            filename_prefix), 'rank': to_comfy_input(rank), 'lora_type':
            to_comfy_input(lora_type), 'bias_diff': to_comfy_input(
            bias_diff), 'model_diff': to_comfy_input(model_diff),
            'text_encoder_diff': to_comfy_input(text_encoder_diff)},
            'class_type': 'LoraSave'}
        self._add_node(node_id, comfy_json_node)

    def TorchCompileModel(self, model: MODEL, backend: str) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'backend': to_comfy_input(backend)}, 'class_type':
            'TorchCompileModel'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def EmptyMochiLatentVideo(self, width: int, height: int, length: int,
        batch_size: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'length': to_comfy_input(
            length), 'batch_size': to_comfy_input(batch_size)},
            'class_type': 'EmptyMochiLatentVideo'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def SkipLayerGuidanceDiT(self, model: MODEL, double_layers: str,
        single_layers: str, scale: float, start_percent: float, end_percent:
        float, rescaling_scale: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'double_layers': to_comfy_input(double_layers), 'single_layers':
            to_comfy_input(single_layers), 'scale': to_comfy_input(scale),
            'start_percent': to_comfy_input(start_percent), 'end_percent':
            to_comfy_input(end_percent), 'rescaling_scale': to_comfy_input(
            rescaling_scale)}, 'class_type': 'SkipLayerGuidanceDiT'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def SkipLayerGuidanceDiTSimple(self, model: MODEL, double_layers: str,
        single_layers: str, start_percent: float, end_percent: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'double_layers': to_comfy_input(double_layers), 'single_layers':
            to_comfy_input(single_layers), 'start_percent': to_comfy_input(
            start_percent), 'end_percent': to_comfy_input(end_percent)},
            'class_type': 'SkipLayerGuidanceDiTSimple'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def Mahiro(self, model: MODEL) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model)},
            'class_type': 'Mahiro'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def EmptyLTXVLatentVideo(self, width: int, height: int, length: int,
        batch_size: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'length': to_comfy_input(
            length), 'batch_size': to_comfy_input(batch_size)},
            'class_type': 'EmptyLTXVLatentVideo'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def LTXVImgToVideo(self, positive: CONDITIONING, negative: CONDITIONING,
        vae: VAE, image: IMAGE, width: int, height: int, length: int,
        batch_size: int, strength: float) ->(CONDITIONING, CONDITIONING, LATENT
        ):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'image': to_comfy_input(image), 'width': to_comfy_input(
            width), 'height': to_comfy_input(height), 'length':
            to_comfy_input(length), 'batch_size': to_comfy_input(batch_size
            ), 'strength': to_comfy_input(strength)}, 'class_type':
            'LTXVImgToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def ModelSamplingLTXV(self, model: MODEL, max_shift: float, base_shift:
        float, latent: LATENT) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'max_shift': to_comfy_input(max_shift), 'base_shift':
            to_comfy_input(base_shift), 'latent': to_comfy_input(latent)},
            'class_type': 'ModelSamplingLTXV'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def LTXVConditioning(self, positive: CONDITIONING, negative:
        CONDITIONING, frame_rate: float) ->(CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'frame_rate':
            to_comfy_input(frame_rate)}, 'class_type': 'LTXVConditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def LTXVScheduler(self, steps: int, max_shift: float, base_shift: float,
        stretch: bool, terminal: float, latent: LATENT) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'steps': to_comfy_input(steps),
            'max_shift': to_comfy_input(max_shift), 'base_shift':
            to_comfy_input(base_shift), 'stretch': to_comfy_input(stretch),
            'terminal': to_comfy_input(terminal), 'latent': to_comfy_input(
            latent)}, 'class_type': 'LTXVScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def LTXVAddGuide(self, positive: CONDITIONING, negative: CONDITIONING,
        vae: VAE, latent: LATENT, image: IMAGE, frame_idx: int, strength: float
        ) ->(CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'latent': to_comfy_input(latent), 'image': to_comfy_input(
            image), 'frame_idx': to_comfy_input(frame_idx), 'strength':
            to_comfy_input(strength)}, 'class_type': 'LTXVAddGuide'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def LTXVPreprocess(self, image: IMAGE, img_compression: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'img_compression': to_comfy_input(img_compression)},
            'class_type': 'LTXVPreprocess'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LTXVCropGuides(self, positive: CONDITIONING, negative: CONDITIONING,
        latent: LATENT) ->(CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'latent': to_comfy_input(
            latent)}, 'class_type': 'LTXVCropGuides'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def CreateHookLora(self, lora_name: str, strength_model: float,
        strength_clip: float, prev_hooks: HOOKS) ->HOOKS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'lora_name': to_comfy_input(lora_name
            ), 'strength_model': to_comfy_input(strength_model),
            'strength_clip': to_comfy_input(strength_clip), 'prev_hooks':
            to_comfy_input(prev_hooks)}, 'class_type': 'CreateHookLora'}
        self._add_node(node_id, comfy_json_node)
        return HOOKS(node_id, 0)

    def CreateHookLoraModelOnly(self, lora_name: str, strength_model: float,
        prev_hooks: HOOKS) ->HOOKS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'lora_name': to_comfy_input(lora_name
            ), 'strength_model': to_comfy_input(strength_model),
            'prev_hooks': to_comfy_input(prev_hooks)}, 'class_type':
            'CreateHookLoraModelOnly'}
        self._add_node(node_id, comfy_json_node)
        return HOOKS(node_id, 0)

    def CreateHookModelAsLora(self, ckpt_name: str, strength_model: float,
        strength_clip: float, prev_hooks: HOOKS) ->HOOKS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'ckpt_name': to_comfy_input(ckpt_name
            ), 'strength_model': to_comfy_input(strength_model),
            'strength_clip': to_comfy_input(strength_clip), 'prev_hooks':
            to_comfy_input(prev_hooks)}, 'class_type': 'CreateHookModelAsLora'}
        self._add_node(node_id, comfy_json_node)
        return HOOKS(node_id, 0)

    def CreateHookModelAsLoraModelOnly(self, ckpt_name: str, strength_model:
        float, prev_hooks: HOOKS) ->HOOKS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'ckpt_name': to_comfy_input(ckpt_name
            ), 'strength_model': to_comfy_input(strength_model),
            'prev_hooks': to_comfy_input(prev_hooks)}, 'class_type':
            'CreateHookModelAsLoraModelOnly'}
        self._add_node(node_id, comfy_json_node)
        return HOOKS(node_id, 0)

    def SetHookKeyframes(self, hooks: HOOKS, hook_kf: HOOK_KEYFRAMES) ->HOOKS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'hooks': to_comfy_input(hooks),
            'hook_kf': to_comfy_input(hook_kf)}, 'class_type':
            'SetHookKeyframes'}
        self._add_node(node_id, comfy_json_node)
        return HOOKS(node_id, 0)

    def CreateHookKeyframe(self, strength_mult: float, start_percent: float,
        prev_hook_kf: HOOK_KEYFRAMES) ->HOOK_KEYFRAMES:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'strength_mult': to_comfy_input(
            strength_mult), 'start_percent': to_comfy_input(start_percent),
            'prev_hook_kf': to_comfy_input(prev_hook_kf)}, 'class_type':
            'CreateHookKeyframe'}
        self._add_node(node_id, comfy_json_node)
        return HOOK_KEYFRAMES(node_id, 0)

    def CreateHookKeyframesInterpolated(self, strength_start: float,
        strength_end: float, interpolation: str, start_percent: float,
        end_percent: float, keyframes_count: int, print_keyframes: bool,
        prev_hook_kf: HOOK_KEYFRAMES) ->HOOK_KEYFRAMES:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'strength_start': to_comfy_input(
            strength_start), 'strength_end': to_comfy_input(strength_end),
            'interpolation': to_comfy_input(interpolation), 'start_percent':
            to_comfy_input(start_percent), 'end_percent': to_comfy_input(
            end_percent), 'keyframes_count': to_comfy_input(keyframes_count
            ), 'print_keyframes': to_comfy_input(print_keyframes),
            'prev_hook_kf': to_comfy_input(prev_hook_kf)}, 'class_type':
            'CreateHookKeyframesInterpolated'}
        self._add_node(node_id, comfy_json_node)
        return HOOK_KEYFRAMES(node_id, 0)

    def CreateHookKeyframesFromFloats(self, floats_strength: FLOATS,
        start_percent: float, end_percent: float, print_keyframes: bool,
        prev_hook_kf: HOOK_KEYFRAMES) ->HOOK_KEYFRAMES:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'floats_strength': to_comfy_input(
            floats_strength), 'start_percent': to_comfy_input(start_percent
            ), 'end_percent': to_comfy_input(end_percent),
            'print_keyframes': to_comfy_input(print_keyframes),
            'prev_hook_kf': to_comfy_input(prev_hook_kf)}, 'class_type':
            'CreateHookKeyframesFromFloats'}
        self._add_node(node_id, comfy_json_node)
        return HOOK_KEYFRAMES(node_id, 0)

    def CombineHooks2(self, hooks_A: HOOKS, hooks_B: HOOKS) ->HOOKS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'hooks_A': to_comfy_input(hooks_A),
            'hooks_B': to_comfy_input(hooks_B)}, 'class_type': 'CombineHooks2'}
        self._add_node(node_id, comfy_json_node)
        return HOOKS(node_id, 0)

    def CombineHooks4(self, hooks_A: HOOKS, hooks_B: HOOKS, hooks_C: HOOKS,
        hooks_D: HOOKS) ->HOOKS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'hooks_A': to_comfy_input(hooks_A),
            'hooks_B': to_comfy_input(hooks_B), 'hooks_C': to_comfy_input(
            hooks_C), 'hooks_D': to_comfy_input(hooks_D)}, 'class_type':
            'CombineHooks4'}
        self._add_node(node_id, comfy_json_node)
        return HOOKS(node_id, 0)

    def CombineHooks8(self, hooks_A: HOOKS, hooks_B: HOOKS, hooks_C: HOOKS,
        hooks_D: HOOKS, hooks_E: HOOKS, hooks_F: HOOKS, hooks_G: HOOKS,
        hooks_H: HOOKS) ->HOOKS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'hooks_A': to_comfy_input(hooks_A),
            'hooks_B': to_comfy_input(hooks_B), 'hooks_C': to_comfy_input(
            hooks_C), 'hooks_D': to_comfy_input(hooks_D), 'hooks_E':
            to_comfy_input(hooks_E), 'hooks_F': to_comfy_input(hooks_F),
            'hooks_G': to_comfy_input(hooks_G), 'hooks_H': to_comfy_input(
            hooks_H)}, 'class_type': 'CombineHooks8'}
        self._add_node(node_id, comfy_json_node)
        return HOOKS(node_id, 0)

    def ConditioningSetProperties(self, cond_NEW: CONDITIONING, strength:
        float, set_cond_area: str, mask: MASK, hooks: HOOKS, timesteps:
        TIMESTEPS_RANGE) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'cond_NEW': to_comfy_input(cond_NEW),
            'strength': to_comfy_input(strength), 'set_cond_area':
            to_comfy_input(set_cond_area), 'mask': to_comfy_input(mask),
            'hooks': to_comfy_input(hooks), 'timesteps': to_comfy_input(
            timesteps)}, 'class_type': 'ConditioningSetProperties'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ConditioningSetPropertiesAndCombine(self, cond: CONDITIONING,
        cond_NEW: CONDITIONING, strength: float, set_cond_area: str, mask:
        MASK, hooks: HOOKS, timesteps: TIMESTEPS_RANGE) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'cond': to_comfy_input(cond),
            'cond_NEW': to_comfy_input(cond_NEW), 'strength':
            to_comfy_input(strength), 'set_cond_area': to_comfy_input(
            set_cond_area), 'mask': to_comfy_input(mask), 'hooks':
            to_comfy_input(hooks), 'timesteps': to_comfy_input(timesteps)},
            'class_type': 'ConditioningSetPropertiesAndCombine'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def PairConditioningSetProperties(self, positive_NEW: CONDITIONING,
        negative_NEW: CONDITIONING, strength: float, set_cond_area: str,
        mask: MASK, hooks: HOOKS, timesteps: TIMESTEPS_RANGE) ->(CONDITIONING,
        CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive_NEW': to_comfy_input(
            positive_NEW), 'negative_NEW': to_comfy_input(negative_NEW),
            'strength': to_comfy_input(strength), 'set_cond_area':
            to_comfy_input(set_cond_area), 'mask': to_comfy_input(mask),
            'hooks': to_comfy_input(hooks), 'timesteps': to_comfy_input(
            timesteps)}, 'class_type': 'PairConditioningSetProperties'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def PairConditioningSetPropertiesAndCombine(self, positive:
        CONDITIONING, negative: CONDITIONING, positive_NEW: CONDITIONING,
        negative_NEW: CONDITIONING, strength: float, set_cond_area: str,
        mask: MASK, hooks: HOOKS, timesteps: TIMESTEPS_RANGE) ->(CONDITIONING,
        CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'positive_NEW':
            to_comfy_input(positive_NEW), 'negative_NEW': to_comfy_input(
            negative_NEW), 'strength': to_comfy_input(strength),
            'set_cond_area': to_comfy_input(set_cond_area), 'mask':
            to_comfy_input(mask), 'hooks': to_comfy_input(hooks),
            'timesteps': to_comfy_input(timesteps)}, 'class_type':
            'PairConditioningSetPropertiesAndCombine'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def ConditioningSetDefaultCombine(self, cond: CONDITIONING,
        cond_DEFAULT: CONDITIONING, hooks: HOOKS) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'cond': to_comfy_input(cond),
            'cond_DEFAULT': to_comfy_input(cond_DEFAULT), 'hooks':
            to_comfy_input(hooks)}, 'class_type':
            'ConditioningSetDefaultCombine'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def PairConditioningSetDefaultCombine(self, positive: CONDITIONING,
        negative: CONDITIONING, positive_DEFAULT: CONDITIONING,
        negative_DEFAULT: CONDITIONING, hooks: HOOKS) ->(CONDITIONING,
        CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'positive_DEFAULT':
            to_comfy_input(positive_DEFAULT), 'negative_DEFAULT':
            to_comfy_input(negative_DEFAULT), 'hooks': to_comfy_input(hooks
            )}, 'class_type': 'PairConditioningSetDefaultCombine'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def PairConditioningCombine(self, positive_A: CONDITIONING, negative_A:
        CONDITIONING, positive_B: CONDITIONING, negative_B: CONDITIONING) ->(
        CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive_A': to_comfy_input(
            positive_A), 'negative_A': to_comfy_input(negative_A),
            'positive_B': to_comfy_input(positive_B), 'negative_B':
            to_comfy_input(negative_B)}, 'class_type':
            'PairConditioningCombine'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def SetClipHooks(self, clip: CLIP, apply_to_conds: bool, schedule_clip:
        bool, hooks: HOOKS) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'apply_to_conds': to_comfy_input(apply_to_conds),
            'schedule_clip': to_comfy_input(schedule_clip), 'hooks':
            to_comfy_input(hooks)}, 'class_type': 'SetClipHooks'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def ConditioningTimestepsRange(self, start_percent: float, end_percent:
        float) ->(TIMESTEPS_RANGE, TIMESTEPS_RANGE, TIMESTEPS_RANGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'start_percent': to_comfy_input(
            start_percent), 'end_percent': to_comfy_input(end_percent)},
            'class_type': 'ConditioningTimestepsRange'}
        self._add_node(node_id, comfy_json_node)
        return TIMESTEPS_RANGE(node_id, 0), TIMESTEPS_RANGE(node_id, 1
            ), TIMESTEPS_RANGE(node_id, 2)

    def Load3D(self, model_file: str, image: LOAD_3D, width: int, height: int
        ) ->(IMAGE, MASK, StrNodeOutput, IMAGE, IMAGE, LOAD3D_CAMERA, VIDEO):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_file': to_comfy_input(
            model_file), 'image': to_comfy_input(image), 'width':
            to_comfy_input(width), 'height': to_comfy_input(height)},
            'class_type': 'Load3D'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1), StrNodeOutput(node_id, 2
            ), IMAGE(node_id, 3), IMAGE(node_id, 4), LOAD3D_CAMERA(node_id, 5
            ), VIDEO(node_id, 6)

    def Load3DAnimation(self, model_file: str, image: LOAD_3D_ANIMATION,
        width: int, height: int) ->(IMAGE, MASK, StrNodeOutput, IMAGE,
        LOAD3D_CAMERA, VIDEO):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_file': to_comfy_input(
            model_file), 'image': to_comfy_input(image), 'width':
            to_comfy_input(width), 'height': to_comfy_input(height)},
            'class_type': 'Load3DAnimation'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1), StrNodeOutput(node_id, 2
            ), IMAGE(node_id, 3), LOAD3D_CAMERA(node_id, 4), VIDEO(node_id, 5)

    def Preview3D(self, model_file: str, camera_info: LOAD3D_CAMERA) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_file': to_comfy_input(
            model_file), 'camera_info': to_comfy_input(camera_info)},
            'class_type': 'Preview3D'}
        self._add_node(node_id, comfy_json_node)

    def Preview3DAnimation(self, model_file: str, camera_info: LOAD3D_CAMERA
        ) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_file': to_comfy_input(
            model_file), 'camera_info': to_comfy_input(camera_info)},
            'class_type': 'Preview3DAnimation'}
        self._add_node(node_id, comfy_json_node)

    def EmptyCosmosLatentVideo(self, width: int, height: int, length: int,
        batch_size: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'width': to_comfy_input(width),
            'height': to_comfy_input(height), 'length': to_comfy_input(
            length), 'batch_size': to_comfy_input(batch_size)},
            'class_type': 'EmptyCosmosLatentVideo'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def CosmosImageToVideoLatent(self, vae: VAE, width: int, height: int,
        length: int, batch_size: int, start_image: IMAGE, end_image: IMAGE
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'vae': to_comfy_input(vae), 'width':
            to_comfy_input(width), 'height': to_comfy_input(height),
            'length': to_comfy_input(length), 'batch_size': to_comfy_input(
            batch_size), 'start_image': to_comfy_input(start_image),
            'end_image': to_comfy_input(end_image)}, 'class_type':
            'CosmosImageToVideoLatent'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def CosmosPredict2ImageToVideoLatent(self, vae: VAE, width: int, height:
        int, length: int, batch_size: int, start_image: IMAGE, end_image: IMAGE
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'vae': to_comfy_input(vae), 'width':
            to_comfy_input(width), 'height': to_comfy_input(height),
            'length': to_comfy_input(length), 'batch_size': to_comfy_input(
            batch_size), 'start_image': to_comfy_input(start_image),
            'end_image': to_comfy_input(end_image)}, 'class_type':
            'CosmosPredict2ImageToVideoLatent'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def SaveWEBM(self, images: IMAGE, filename_prefix: str, codec: str, fps:
        float, crf: float) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'filename_prefix': to_comfy_input(filename_prefix), 'codec':
            to_comfy_input(codec), 'fps': to_comfy_input(fps), 'crf':
            to_comfy_input(crf)}, 'class_type': 'SaveWEBM'}
        self._add_node(node_id, comfy_json_node)

    def SaveVideo(self, video: VIDEO, filename_prefix: str, format: str,
        codec: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'video': to_comfy_input(video),
            'filename_prefix': to_comfy_input(filename_prefix), 'format':
            to_comfy_input(format), 'codec': to_comfy_input(codec)},
            'class_type': 'SaveVideo'}
        self._add_node(node_id, comfy_json_node)

    def CreateVideo(self, images: IMAGE, fps: float, audio: AUDIO) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'fps': to_comfy_input(fps), 'audio': to_comfy_input(audio)},
            'class_type': 'CreateVideo'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def GetVideoComponents(self, video: VIDEO) ->(IMAGE, AUDIO, FloatNodeOutput
        ):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'video': to_comfy_input(video)},
            'class_type': 'GetVideoComponents'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), AUDIO(node_id, 1), FloatNodeOutput(node_id, 2
            )

    def LoadVideo(self, file: str) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'file': to_comfy_input(file)},
            'class_type': 'LoadVideo'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def CLIPTextEncodeLumina2(self, system_prompt: str, user_prompt: str,
        clip: CLIP) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'system_prompt': to_comfy_input(
            system_prompt), 'user_prompt': to_comfy_input(user_prompt),
            'clip': to_comfy_input(clip)}, 'class_type':
            'CLIPTextEncodeLumina2'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def RenormCFG(self, model: MODEL, cfg_trunc: float, renorm_cfg: float
        ) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'cfg_trunc': to_comfy_input(cfg_trunc), 'renorm_cfg':
            to_comfy_input(renorm_cfg)}, 'class_type': 'RenormCFG'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def WanImageToVideo(self, positive: CONDITIONING, negative:
        CONDITIONING, vae: VAE, width: int, height: int, length: int,
        batch_size: int, clip_vision_output: CLIP_VISION_OUTPUT,
        start_image: IMAGE) ->(CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'width': to_comfy_input(width), 'height': to_comfy_input(
            height), 'length': to_comfy_input(length), 'batch_size':
            to_comfy_input(batch_size), 'clip_vision_output':
            to_comfy_input(clip_vision_output), 'start_image':
            to_comfy_input(start_image)}, 'class_type': 'WanImageToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def WanFunControlToVideo(self, positive: CONDITIONING, negative:
        CONDITIONING, vae: VAE, width: int, height: int, length: int,
        batch_size: int, clip_vision_output: CLIP_VISION_OUTPUT,
        start_image: IMAGE, control_video: IMAGE) ->(CONDITIONING,
        CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'width': to_comfy_input(width), 'height': to_comfy_input(
            height), 'length': to_comfy_input(length), 'batch_size':
            to_comfy_input(batch_size), 'clip_vision_output':
            to_comfy_input(clip_vision_output), 'start_image':
            to_comfy_input(start_image), 'control_video': to_comfy_input(
            control_video)}, 'class_type': 'WanFunControlToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def WanFunInpaintToVideo(self, positive: CONDITIONING, negative:
        CONDITIONING, vae: VAE, width: int, height: int, length: int,
        batch_size: int, clip_vision_output: CLIP_VISION_OUTPUT,
        start_image: IMAGE, end_image: IMAGE) ->(CONDITIONING, CONDITIONING,
        LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'width': to_comfy_input(width), 'height': to_comfy_input(
            height), 'length': to_comfy_input(length), 'batch_size':
            to_comfy_input(batch_size), 'clip_vision_output':
            to_comfy_input(clip_vision_output), 'start_image':
            to_comfy_input(start_image), 'end_image': to_comfy_input(
            end_image)}, 'class_type': 'WanFunInpaintToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def WanFirstLastFrameToVideo(self, positive: CONDITIONING, negative:
        CONDITIONING, vae: VAE, width: int, height: int, length: int,
        batch_size: int, clip_vision_start_image: CLIP_VISION_OUTPUT,
        clip_vision_end_image: CLIP_VISION_OUTPUT, start_image: IMAGE,
        end_image: IMAGE) ->(CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'width': to_comfy_input(width), 'height': to_comfy_input(
            height), 'length': to_comfy_input(length), 'batch_size':
            to_comfy_input(batch_size), 'clip_vision_start_image':
            to_comfy_input(clip_vision_start_image),
            'clip_vision_end_image': to_comfy_input(clip_vision_end_image),
            'start_image': to_comfy_input(start_image), 'end_image':
            to_comfy_input(end_image)}, 'class_type':
            'WanFirstLastFrameToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def WanVaceToVideo(self, positive: CONDITIONING, negative: CONDITIONING,
        vae: VAE, width: int, height: int, length: int, batch_size: int,
        strength: float, control_video: IMAGE, control_masks: MASK,
        reference_image: IMAGE) ->(CONDITIONING, CONDITIONING, LATENT,
        IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'width': to_comfy_input(width), 'height': to_comfy_input(
            height), 'length': to_comfy_input(length), 'batch_size':
            to_comfy_input(batch_size), 'strength': to_comfy_input(strength
            ), 'control_video': to_comfy_input(control_video),
            'control_masks': to_comfy_input(control_masks),
            'reference_image': to_comfy_input(reference_image)},
            'class_type': 'WanVaceToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2), IntNodeOutput(node_id, 3)

    def TrimVideoLatent(self, samples: LATENT, trim_amount: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'trim_amount': to_comfy_input(trim_amount)}, 'class_type':
            'TrimVideoLatent'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def WanCameraImageToVideo(self, positive: CONDITIONING, negative:
        CONDITIONING, vae: VAE, width: int, height: int, length: int,
        batch_size: int, clip_vision_output: CLIP_VISION_OUTPUT,
        start_image: IMAGE, camera_conditions: WAN_CAMERA_EMBEDDING) ->(
        CONDITIONING, CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'width': to_comfy_input(width), 'height': to_comfy_input(
            height), 'length': to_comfy_input(length), 'batch_size':
            to_comfy_input(batch_size), 'clip_vision_output':
            to_comfy_input(clip_vision_output), 'start_image':
            to_comfy_input(start_image), 'camera_conditions':
            to_comfy_input(camera_conditions)}, 'class_type':
            'WanCameraImageToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1), LATENT(
            node_id, 2)

    def WanPhantomSubjectToVideo(self, positive: CONDITIONING, negative:
        CONDITIONING, vae: VAE, width: int, height: int, length: int,
        batch_size: int, images: IMAGE) ->(CONDITIONING, CONDITIONING,
        CONDITIONING, LATENT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'vae': to_comfy_input(vae
            ), 'width': to_comfy_input(width), 'height': to_comfy_input(
            height), 'length': to_comfy_input(length), 'batch_size':
            to_comfy_input(batch_size), 'images': to_comfy_input(images)},
            'class_type': 'WanPhantomSubjectToVideo'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1
            ), CONDITIONING(node_id, 2), LATENT(node_id, 3)

    def LotusConditioning(self) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {}, 'class_type': 'LotusConditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def EmptyLatentHunyuan3Dv2(self, resolution: int, batch_size: int
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'resolution': to_comfy_input(
            resolution), 'batch_size': to_comfy_input(batch_size)},
            'class_type': 'EmptyLatentHunyuan3Dv2'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def Hunyuan3Dv2Conditioning(self, clip_vision_output: CLIP_VISION_OUTPUT
        ) ->(CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_vision_output': to_comfy_input(
            clip_vision_output)}, 'class_type': 'Hunyuan3Dv2Conditioning'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def Hunyuan3Dv2ConditioningMultiView(self, front: CLIP_VISION_OUTPUT,
        left: CLIP_VISION_OUTPUT, back: CLIP_VISION_OUTPUT, right:
        CLIP_VISION_OUTPUT) ->(CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'front': to_comfy_input(front),
            'left': to_comfy_input(left), 'back': to_comfy_input(back),
            'right': to_comfy_input(right)}, 'class_type':
            'Hunyuan3Dv2ConditioningMultiView'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0), CONDITIONING(node_id, 1)

    def VAEDecodeHunyuan3D(self, samples: LATENT, vae: VAE, num_chunks: int,
        octree_resolution: int) ->VOXEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'vae': to_comfy_input(vae), 'num_chunks': to_comfy_input(
            num_chunks), 'octree_resolution': to_comfy_input(
            octree_resolution)}, 'class_type': 'VAEDecodeHunyuan3D'}
        self._add_node(node_id, comfy_json_node)
        return VOXEL(node_id, 0)

    def VoxelToMeshBasic(self, voxel: VOXEL, threshold: float) ->MESH:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'voxel': to_comfy_input(voxel),
            'threshold': to_comfy_input(threshold)}, 'class_type':
            'VoxelToMeshBasic'}
        self._add_node(node_id, comfy_json_node)
        return MESH(node_id, 0)

    def VoxelToMesh(self, voxel: VOXEL, algorithm: str, threshold: float
        ) ->MESH:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'voxel': to_comfy_input(voxel),
            'algorithm': to_comfy_input(algorithm), 'threshold':
            to_comfy_input(threshold)}, 'class_type': 'VoxelToMesh'}
        self._add_node(node_id, comfy_json_node)
        return MESH(node_id, 0)

    def SaveGLB(self, mesh: MESH, filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mesh': to_comfy_input(mesh),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'SaveGLB'}
        self._add_node(node_id, comfy_json_node)

    def PrimitiveString(self, value: str) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'PrimitiveString'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def PrimitiveStringMultiline(self, value: str) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'PrimitiveStringMultiline'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def PrimitiveInt(self, value: int) ->IntNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'PrimitiveInt'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0)

    def PrimitiveFloat(self, value: float) ->FloatNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'PrimitiveFloat'}
        self._add_node(node_id, comfy_json_node)
        return FloatNodeOutput(node_id, 0)

    def PrimitiveBoolean(self, value: bool) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'PrimitiveBoolean'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def CFGZeroStar(self, model: MODEL) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model)},
            'class_type': 'CFGZeroStar'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def CFGNorm(self, model: MODEL, strength: float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'strength': to_comfy_input(strength)}, 'class_type': 'CFGNorm'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def OptimalStepsScheduler(self, model_type: str, steps: int, denoise: float
        ) ->SIGMAS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_type': to_comfy_input(
            model_type), 'steps': to_comfy_input(steps), 'denoise':
            to_comfy_input(denoise)}, 'class_type': 'OptimalStepsScheduler'}
        self._add_node(node_id, comfy_json_node)
        return SIGMAS(node_id, 0)

    def QuadrupleCLIPLoader(self, clip_name1: str, clip_name2: str,
        clip_name3: str, clip_name4: str) ->CLIP:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip_name1': to_comfy_input(
            clip_name1), 'clip_name2': to_comfy_input(clip_name2),
            'clip_name3': to_comfy_input(clip_name3), 'clip_name4':
            to_comfy_input(clip_name4)}, 'class_type': 'QuadrupleCLIPLoader'}
        self._add_node(node_id, comfy_json_node)
        return CLIP(node_id, 0)

    def CLIPTextEncodeHiDream(self, clip: CLIP, clip_l: str, clip_g: str,
        t5xxl: str, llama: str) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip),
            'clip_l': to_comfy_input(clip_l), 'clip_g': to_comfy_input(
            clip_g), 't5xxl': to_comfy_input(t5xxl), 'llama':
            to_comfy_input(llama)}, 'class_type': 'CLIPTextEncodeHiDream'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def FreSca(self, model: MODEL, scale_low: float, scale_high: float,
        freq_cutoff: int) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'scale_low': to_comfy_input(scale_low), 'scale_high':
            to_comfy_input(scale_high), 'freq_cutoff': to_comfy_input(
            freq_cutoff)}, 'class_type': 'FreSca'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def APG(self, model: MODEL, eta: float, norm_threshold: float, momentum:
        float) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model), 'eta':
            to_comfy_input(eta), 'norm_threshold': to_comfy_input(
            norm_threshold), 'momentum': to_comfy_input(momentum)},
            'class_type': 'APG'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def PreviewAny(self, source: AnyNodeOutput) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'source': to_comfy_input(source)},
            'class_type': 'PreviewAny'}
        self._add_node(node_id, comfy_json_node)

    def TextEncodeAceStepAudio(self, clip: CLIP, tags: str, lyrics: str,
        lyrics_strength: float) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'clip': to_comfy_input(clip), 'tags':
            to_comfy_input(tags), 'lyrics': to_comfy_input(lyrics),
            'lyrics_strength': to_comfy_input(lyrics_strength)},
            'class_type': 'TextEncodeAceStepAudio'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def EmptyAceStepLatentAudio(self, seconds: float, batch_size: int
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seconds': to_comfy_input(seconds),
            'batch_size': to_comfy_input(batch_size)}, 'class_type':
            'EmptyAceStepLatentAudio'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def StringConcatenate(self, string_a: str, string_b: str, delimiter: str
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string_a': to_comfy_input(string_a),
            'string_b': to_comfy_input(string_b), 'delimiter':
            to_comfy_input(delimiter)}, 'class_type': 'StringConcatenate'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def StringSubstring(self, string: str, start: int, end: int
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'start': to_comfy_input(start), 'end': to_comfy_input(end)},
            'class_type': 'StringSubstring'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def StringLength(self, string: str) ->IntNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string)},
            'class_type': 'StringLength'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0)

    def CaseConverter(self, string: str, mode: COMBO) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'mode': to_comfy_input(mode)}, 'class_type': 'CaseConverter'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def StringTrim(self, string: str, mode: COMBO) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'mode': to_comfy_input(mode)}, 'class_type': 'StringTrim'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def StringReplace(self, string: str, find: str, replace: str
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'find': to_comfy_input(find), 'replace': to_comfy_input(replace
            )}, 'class_type': 'StringReplace'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def StringContains(self, string: str, substring: str, case_sensitive: bool
        ) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'substring': to_comfy_input(substring), 'case_sensitive':
            to_comfy_input(case_sensitive)}, 'class_type': 'StringContains'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def StringCompare(self, string_a: str, string_b: str, mode: COMBO,
        case_sensitive: bool) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string_a': to_comfy_input(string_a),
            'string_b': to_comfy_input(string_b), 'mode': to_comfy_input(
            mode), 'case_sensitive': to_comfy_input(case_sensitive)},
            'class_type': 'StringCompare'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def RegexMatch(self, string: str, regex_pattern: str, case_insensitive:
        bool, multiline: bool, dotall: bool) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'regex_pattern': to_comfy_input(regex_pattern),
            'case_insensitive': to_comfy_input(case_insensitive),
            'multiline': to_comfy_input(multiline), 'dotall':
            to_comfy_input(dotall)}, 'class_type': 'RegexMatch'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def RegexExtract(self, string: str, regex_pattern: str, mode: COMBO,
        case_insensitive: bool, multiline: bool, dotall: bool, group_index: int
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'regex_pattern': to_comfy_input(regex_pattern), 'mode':
            to_comfy_input(mode), 'case_insensitive': to_comfy_input(
            case_insensitive), 'multiline': to_comfy_input(multiline),
            'dotall': to_comfy_input(dotall), 'group_index': to_comfy_input
            (group_index)}, 'class_type': 'RegexExtract'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def RegexReplace(self, string: str, regex_pattern: str, replace: str,
        case_insensitive: bool, multiline: bool, dotall: bool, count: int
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'regex_pattern': to_comfy_input(regex_pattern), 'replace':
            to_comfy_input(replace), 'case_insensitive': to_comfy_input(
            case_insensitive), 'multiline': to_comfy_input(multiline),
            'dotall': to_comfy_input(dotall), 'count': to_comfy_input(count
            )}, 'class_type': 'RegexReplace'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def WanCameraEmbedding(self, camera_pose: str, width: int, height: int,
        length: int, speed: float, fx: float, fy: float, cx: float, cy: float
        ) ->(WAN_CAMERA_EMBEDDING, IntNodeOutput, IntNodeOutput, IntNodeOutput
        ):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'camera_pose': to_comfy_input(
            camera_pose), 'width': to_comfy_input(width), 'height':
            to_comfy_input(height), 'length': to_comfy_input(length),
            'speed': to_comfy_input(speed), 'fx': to_comfy_input(fx), 'fy':
            to_comfy_input(fy), 'cx': to_comfy_input(cx), 'cy':
            to_comfy_input(cy)}, 'class_type': 'WanCameraEmbedding'}
        self._add_node(node_id, comfy_json_node)
        return WAN_CAMERA_EMBEDDING(node_id, 0), IntNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2), IntNodeOutput(node_id, 3)

    def ReferenceLatent(self, conditioning: CONDITIONING, latent: LATENT
        ) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning': to_comfy_input(
            conditioning), 'latent': to_comfy_input(latent)}, 'class_type':
            'ReferenceLatent'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def TCFG(self, model: MODEL) ->MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model)},
            'class_type': 'TCFG'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0)

    def IdeogramV1(self, prompt: str, turbo: bool, aspect_ratio: COMBO,
        magic_prompt_option: COMBO, seed: int, negative_prompt: str,
        num_images: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'turbo': to_comfy_input(turbo), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'magic_prompt_option': to_comfy_input(
            magic_prompt_option), 'seed': to_comfy_input(seed),
            'negative_prompt': to_comfy_input(negative_prompt),
            'num_images': to_comfy_input(num_images)}, 'class_type':
            'IdeogramV1'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def IdeogramV2(self, prompt: str, turbo: bool, aspect_ratio: COMBO,
        resolution: COMBO, magic_prompt_option: COMBO, seed: int,
        style_type: COMBO, negative_prompt: str, num_images: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'turbo': to_comfy_input(turbo), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'resolution': to_comfy_input(resolution),
            'magic_prompt_option': to_comfy_input(magic_prompt_option),
            'seed': to_comfy_input(seed), 'style_type': to_comfy_input(
            style_type), 'negative_prompt': to_comfy_input(negative_prompt),
            'num_images': to_comfy_input(num_images)}, 'class_type':
            'IdeogramV2'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def IdeogramV3(self, prompt: str, image: IMAGE, mask: MASK,
        aspect_ratio: COMBO, resolution: COMBO, magic_prompt_option: COMBO,
        seed: int, num_images: int, rendering_speed: COMBO) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'image': to_comfy_input(image), 'mask': to_comfy_input(mask),
            'aspect_ratio': to_comfy_input(aspect_ratio), 'resolution':
            to_comfy_input(resolution), 'magic_prompt_option':
            to_comfy_input(magic_prompt_option), 'seed': to_comfy_input(
            seed), 'num_images': to_comfy_input(num_images),
            'rendering_speed': to_comfy_input(rendering_speed)},
            'class_type': 'IdeogramV3'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def OpenAIDalle2(self, prompt: str, seed: int, size: COMBO, n: int,
        image: IMAGE, mask: MASK) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'seed': to_comfy_input(seed), 'size': to_comfy_input(size), 'n':
            to_comfy_input(n), 'image': to_comfy_input(image), 'mask':
            to_comfy_input(mask)}, 'class_type': 'OpenAIDalle2'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def OpenAIDalle3(self, prompt: str, seed: int, quality: COMBO, style:
        COMBO, size: COMBO) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'seed': to_comfy_input(seed), 'quality': to_comfy_input(quality
            ), 'style': to_comfy_input(style), 'size': to_comfy_input(size)
            }, 'class_type': 'OpenAIDalle3'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def OpenAIGPTImage1(self, prompt: str, seed: int, quality: COMBO,
        background: COMBO, size: COMBO, n: int, image: IMAGE, mask: MASK
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'seed': to_comfy_input(seed), 'quality': to_comfy_input(quality
            ), 'background': to_comfy_input(background), 'size':
            to_comfy_input(size), 'n': to_comfy_input(n), 'image':
            to_comfy_input(image), 'mask': to_comfy_input(mask)},
            'class_type': 'OpenAIGPTImage1'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def OpenAIChatNode(self, prompt: str, persist_context: bool, model:
        COMBO, images: IMAGE, files: OPENAI_INPUT_FILES, advanced_options:
        OPENAI_CHAT_CONFIG) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'persist_context': to_comfy_input(persist_context), 'model':
            to_comfy_input(model), 'images': to_comfy_input(images),
            'files': to_comfy_input(files), 'advanced_options':
            to_comfy_input(advanced_options)}, 'class_type': 'OpenAIChatNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def OpenAIInputFiles(self, file: COMBO, OPENAI_INPUT_FILES:
        OPENAI_INPUT_FILES) ->OPENAI_INPUT_FILES:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'file': to_comfy_input(file),
            'OPENAI_INPUT_FILES': to_comfy_input(OPENAI_INPUT_FILES)},
            'class_type': 'OpenAIInputFiles'}
        self._add_node(node_id, comfy_json_node)
        return OPENAI_INPUT_FILES(node_id, 0)

    def OpenAIChatConfig(self, truncation: COMBO, max_output_tokens: int,
        instructions: str) ->OPENAI_CHAT_CONFIG:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'truncation': to_comfy_input(
            truncation), 'max_output_tokens': to_comfy_input(
            max_output_tokens), 'instructions': to_comfy_input(instructions
            )}, 'class_type': 'OpenAIChatConfig'}
        self._add_node(node_id, comfy_json_node)
        return OPENAI_CHAT_CONFIG(node_id, 0)

    def MinimaxTextToVideoNode(self, prompt_text: str, model: str, seed: int
        ) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt_text': to_comfy_input(
            prompt_text), 'model': to_comfy_input(model), 'seed':
            to_comfy_input(seed)}, 'class_type': 'MinimaxTextToVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def MinimaxImageToVideoNode(self, image: IMAGE, prompt_text: str, model:
        str, seed: int) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt_text': to_comfy_input(prompt_text), 'model':
            to_comfy_input(model), 'seed': to_comfy_input(seed)},
            'class_type': 'MinimaxImageToVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def VeoVideoGenerationNode(self, prompt: str, aspect_ratio: COMBO,
        negative_prompt: str, duration_seconds: int, enhance_prompt: bool,
        person_generation: COMBO, seed: int, image: IMAGE) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'aspect_ratio': to_comfy_input(aspect_ratio), 'negative_prompt':
            to_comfy_input(negative_prompt), 'duration_seconds':
            to_comfy_input(duration_seconds), 'enhance_prompt':
            to_comfy_input(enhance_prompt), 'person_generation':
            to_comfy_input(person_generation), 'seed': to_comfy_input(seed),
            'image': to_comfy_input(image)}, 'class_type':
            'VeoVideoGenerationNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def KlingCameraControls(self, camera_control_type: COMBO,
        horizontal_movement: float, vertical_movement: float, pan: float,
        tilt: float, roll: float, zoom: float) ->CAMERA_CONTROL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'camera_control_type': to_comfy_input
            (camera_control_type), 'horizontal_movement': to_comfy_input(
            horizontal_movement), 'vertical_movement': to_comfy_input(
            vertical_movement), 'pan': to_comfy_input(pan), 'tilt':
            to_comfy_input(tilt), 'roll': to_comfy_input(roll), 'zoom':
            to_comfy_input(zoom)}, 'class_type': 'KlingCameraControls'}
        self._add_node(node_id, comfy_json_node)
        return CAMERA_CONTROL(node_id, 0)

    def KlingTextToVideoNode(self, prompt: str, negative_prompt: str,
        cfg_scale: float, aspect_ratio: COMBO, mode: str) ->(VIDEO,
        StrNodeOutput, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt), 'cfg_scale':
            to_comfy_input(cfg_scale), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'mode': to_comfy_input(mode)}, 'class_type':
            'KlingTextToVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingImage2VideoNode(self, start_frame: IMAGE, prompt: str,
        negative_prompt: str, model_name: COMBO, cfg_scale: float, mode:
        COMBO, aspect_ratio: COMBO, duration: COMBO) ->(VIDEO,
        StrNodeOutput, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'start_frame': to_comfy_input(
            start_frame), 'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt),
            'model_name': to_comfy_input(model_name), 'cfg_scale':
            to_comfy_input(cfg_scale), 'mode': to_comfy_input(mode),
            'aspect_ratio': to_comfy_input(aspect_ratio), 'duration':
            to_comfy_input(duration)}, 'class_type': 'KlingImage2VideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingCameraControlI2VNode(self, start_frame: IMAGE, prompt: str,
        negative_prompt: str, cfg_scale: float, aspect_ratio: COMBO,
        camera_control: CAMERA_CONTROL) ->(VIDEO, StrNodeOutput, StrNodeOutput
        ):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'start_frame': to_comfy_input(
            start_frame), 'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt), 'cfg_scale':
            to_comfy_input(cfg_scale), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'camera_control': to_comfy_input(camera_control)
            }, 'class_type': 'KlingCameraControlI2VNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingCameraControlT2VNode(self, prompt: str, negative_prompt: str,
        cfg_scale: float, aspect_ratio: COMBO, camera_control: CAMERA_CONTROL
        ) ->(VIDEO, StrNodeOutput, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt), 'cfg_scale':
            to_comfy_input(cfg_scale), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'camera_control': to_comfy_input(camera_control)
            }, 'class_type': 'KlingCameraControlT2VNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingStartEndFrameNode(self, start_frame: IMAGE, end_frame: IMAGE,
        prompt: str, negative_prompt: str, cfg_scale: float, aspect_ratio:
        COMBO, mode: str) ->(VIDEO, StrNodeOutput, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'start_frame': to_comfy_input(
            start_frame), 'end_frame': to_comfy_input(end_frame), 'prompt':
            to_comfy_input(prompt), 'negative_prompt': to_comfy_input(
            negative_prompt), 'cfg_scale': to_comfy_input(cfg_scale),
            'aspect_ratio': to_comfy_input(aspect_ratio), 'mode':
            to_comfy_input(mode)}, 'class_type': 'KlingStartEndFrameNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingVideoExtendNode(self, prompt: str, negative_prompt: str,
        cfg_scale: float, video_id: str) ->(VIDEO, StrNodeOutput, StrNodeOutput
        ):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt), 'cfg_scale':
            to_comfy_input(cfg_scale), 'video_id': to_comfy_input(video_id)
            }, 'class_type': 'KlingVideoExtendNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingLipSyncAudioToVideoNode(self, video: VIDEO, audio: AUDIO,
        voice_language: COMBO) ->(VIDEO, StrNodeOutput, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'video': to_comfy_input(video),
            'audio': to_comfy_input(audio), 'voice_language':
            to_comfy_input(voice_language)}, 'class_type':
            'KlingLipSyncAudioToVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingLipSyncTextToVideoNode(self, video: VIDEO, text: str, voice:
        str, voice_speed: float) ->(VIDEO, StrNodeOutput, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'video': to_comfy_input(video),
            'text': to_comfy_input(text), 'voice': to_comfy_input(voice),
            'voice_speed': to_comfy_input(voice_speed)}, 'class_type':
            'KlingLipSyncTextToVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingVirtualTryOnNode(self, human_image: IMAGE, cloth_image: IMAGE,
        model_name: COMBO) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'human_image': to_comfy_input(
            human_image), 'cloth_image': to_comfy_input(cloth_image),
            'model_name': to_comfy_input(model_name)}, 'class_type':
            'KlingVirtualTryOnNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def KlingImageGenerationNode(self, prompt: str, negative_prompt: str,
        image_type: COMBO, image_fidelity: float, human_fidelity: float,
        model_name: COMBO, aspect_ratio: COMBO, n: int, image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt),
            'image_type': to_comfy_input(image_type), 'image_fidelity':
            to_comfy_input(image_fidelity), 'human_fidelity':
            to_comfy_input(human_fidelity), 'model_name': to_comfy_input(
            model_name), 'aspect_ratio': to_comfy_input(aspect_ratio), 'n':
            to_comfy_input(n), 'image': to_comfy_input(image)},
            'class_type': 'KlingImageGenerationNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def KlingSingleImageVideoEffectNode(self, image: IMAGE, effect_scene:
        COMBO, model_name: COMBO, duration: COMBO) ->(VIDEO, StrNodeOutput,
        StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'effect_scene': to_comfy_input(effect_scene), 'model_name':
            to_comfy_input(model_name), 'duration': to_comfy_input(duration
            )}, 'class_type': 'KlingSingleImageVideoEffectNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1), StrNodeOutput(
            node_id, 2)

    def KlingDualCharacterVideoEffectNode(self, image_left: IMAGE,
        image_right: IMAGE, effect_scene: COMBO, model_name: COMBO, mode:
        COMBO, duration: COMBO) ->(VIDEO, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image_left': to_comfy_input(
            image_left), 'image_right': to_comfy_input(image_right),
            'effect_scene': to_comfy_input(effect_scene), 'model_name':
            to_comfy_input(model_name), 'mode': to_comfy_input(mode),
            'duration': to_comfy_input(duration)}, 'class_type':
            'KlingDualCharacterVideoEffectNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0), StrNodeOutput(node_id, 1)

    def FluxProUltraImageNode(self, prompt: str, prompt_upsampling: bool,
        seed: int, aspect_ratio: str, raw: bool, image_prompt: IMAGE,
        image_prompt_strength: float) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'prompt_upsampling': to_comfy_input(prompt_upsampling), 'seed':
            to_comfy_input(seed), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'raw': to_comfy_input(raw), 'image_prompt':
            to_comfy_input(image_prompt), 'image_prompt_strength':
            to_comfy_input(image_prompt_strength)}, 'class_type':
            'FluxProUltraImageNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def FluxKontextProImageNode(self, prompt: str, aspect_ratio: str,
        guidance: float, steps: int, seed: int, prompt_upsampling: bool,
        input_image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'aspect_ratio': to_comfy_input(aspect_ratio), 'guidance':
            to_comfy_input(guidance), 'steps': to_comfy_input(steps),
            'seed': to_comfy_input(seed), 'prompt_upsampling':
            to_comfy_input(prompt_upsampling), 'input_image':
            to_comfy_input(input_image)}, 'class_type':
            'FluxKontextProImageNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def FluxKontextMaxImageNode(self, prompt: str, aspect_ratio: str,
        guidance: float, steps: int, seed: int, prompt_upsampling: bool,
        input_image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'aspect_ratio': to_comfy_input(aspect_ratio), 'guidance':
            to_comfy_input(guidance), 'steps': to_comfy_input(steps),
            'seed': to_comfy_input(seed), 'prompt_upsampling':
            to_comfy_input(prompt_upsampling), 'input_image':
            to_comfy_input(input_image)}, 'class_type':
            'FluxKontextMaxImageNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def FluxProExpandNode(self, image: IMAGE, prompt: str,
        prompt_upsampling: bool, top: int, bottom: int, left: int, right:
        int, guidance: float, steps: int, seed: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt': to_comfy_input(prompt), 'prompt_upsampling':
            to_comfy_input(prompt_upsampling), 'top': to_comfy_input(top),
            'bottom': to_comfy_input(bottom), 'left': to_comfy_input(left),
            'right': to_comfy_input(right), 'guidance': to_comfy_input(
            guidance), 'steps': to_comfy_input(steps), 'seed':
            to_comfy_input(seed)}, 'class_type': 'FluxProExpandNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def FluxProFillNode(self, image: IMAGE, mask: MASK, prompt: str,
        prompt_upsampling: bool, guidance: float, steps: int, seed: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'mask': to_comfy_input(mask), 'prompt': to_comfy_input(prompt),
            'prompt_upsampling': to_comfy_input(prompt_upsampling),
            'guidance': to_comfy_input(guidance), 'steps': to_comfy_input(
            steps), 'seed': to_comfy_input(seed)}, 'class_type':
            'FluxProFillNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def FluxProCannyNode(self, control_image: IMAGE, prompt: str,
        prompt_upsampling: bool, canny_low_threshold: float,
        canny_high_threshold: float, skip_preprocessing: bool, guidance:
        float, steps: int, seed: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'control_image': to_comfy_input(
            control_image), 'prompt': to_comfy_input(prompt),
            'prompt_upsampling': to_comfy_input(prompt_upsampling),
            'canny_low_threshold': to_comfy_input(canny_low_threshold),
            'canny_high_threshold': to_comfy_input(canny_high_threshold),
            'skip_preprocessing': to_comfy_input(skip_preprocessing),
            'guidance': to_comfy_input(guidance), 'steps': to_comfy_input(
            steps), 'seed': to_comfy_input(seed)}, 'class_type':
            'FluxProCannyNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def FluxProDepthNode(self, control_image: IMAGE, prompt: str,
        prompt_upsampling: bool, skip_preprocessing: bool, guidance: float,
        steps: int, seed: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'control_image': to_comfy_input(
            control_image), 'prompt': to_comfy_input(prompt),
            'prompt_upsampling': to_comfy_input(prompt_upsampling),
            'skip_preprocessing': to_comfy_input(skip_preprocessing),
            'guidance': to_comfy_input(guidance), 'steps': to_comfy_input(
            steps), 'seed': to_comfy_input(seed)}, 'class_type':
            'FluxProDepthNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LumaImageNode(self, prompt: str, model: str, aspect_ratio: str,
        seed: int, style_image_weight: float, image_luma_ref: LUMA_REF,
        style_image: IMAGE, character_image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'model': to_comfy_input(model), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'seed': to_comfy_input(seed),
            'style_image_weight': to_comfy_input(style_image_weight),
            'image_luma_ref': to_comfy_input(image_luma_ref), 'style_image':
            to_comfy_input(style_image), 'character_image': to_comfy_input(
            character_image)}, 'class_type': 'LumaImageNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LumaImageModifyNode(self, image: IMAGE, prompt: str, image_weight:
        float, model: str, seed: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt': to_comfy_input(prompt), 'image_weight':
            to_comfy_input(image_weight), 'model': to_comfy_input(model),
            'seed': to_comfy_input(seed)}, 'class_type': 'LumaImageModifyNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LumaVideoNode(self, prompt: str, model: str, aspect_ratio: str,
        resolution: str, duration: str, loop: bool, seed: int,
        luma_concepts: LUMA_CONCEPTS) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'model': to_comfy_input(model), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'resolution': to_comfy_input(resolution),
            'duration': to_comfy_input(duration), 'loop': to_comfy_input(
            loop), 'seed': to_comfy_input(seed), 'luma_concepts':
            to_comfy_input(luma_concepts)}, 'class_type': 'LumaVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def LumaImageToVideoNode(self, prompt: str, model: str, resolution: str,
        duration: str, loop: bool, seed: int, first_image: IMAGE,
        last_image: IMAGE, luma_concepts: LUMA_CONCEPTS) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'model': to_comfy_input(model), 'resolution': to_comfy_input(
            resolution), 'duration': to_comfy_input(duration), 'loop':
            to_comfy_input(loop), 'seed': to_comfy_input(seed),
            'first_image': to_comfy_input(first_image), 'last_image':
            to_comfy_input(last_image), 'luma_concepts': to_comfy_input(
            luma_concepts)}, 'class_type': 'LumaImageToVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def LumaReferenceNode(self, image: IMAGE, weight: float, luma_ref: LUMA_REF
        ) ->LUMA_REF:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'weight': to_comfy_input(weight), 'luma_ref': to_comfy_input(
            luma_ref)}, 'class_type': 'LumaReferenceNode'}
        self._add_node(node_id, comfy_json_node)
        return LUMA_REF(node_id, 0)

    def LumaConceptsNode(self, concept1: str, concept2: str, concept3: str,
        concept4: str, luma_concepts: LUMA_CONCEPTS) ->LUMA_CONCEPTS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'concept1': to_comfy_input(concept1),
            'concept2': to_comfy_input(concept2), 'concept3':
            to_comfy_input(concept3), 'concept4': to_comfy_input(concept4),
            'luma_concepts': to_comfy_input(luma_concepts)}, 'class_type':
            'LumaConceptsNode'}
        self._add_node(node_id, comfy_json_node)
        return LUMA_CONCEPTS(node_id, 0)

    def RecraftTextToImageNode(self, prompt: str, size: str, n: int, seed:
        int, recraft_style: RECRAFT_V3_STYLE, negative_prompt: str,
        recraft_controls: RECRAFT_CONTROLS) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'size': to_comfy_input(size), 'n': to_comfy_input(n), 'seed':
            to_comfy_input(seed), 'recraft_style': to_comfy_input(
            recraft_style), 'negative_prompt': to_comfy_input(
            negative_prompt), 'recraft_controls': to_comfy_input(
            recraft_controls)}, 'class_type': 'RecraftTextToImageNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RecraftImageToImageNode(self, image: IMAGE, prompt: str, n: int,
        strength: float, seed: int, recraft_style: RECRAFT_V3_STYLE,
        negative_prompt: str, recraft_controls: RECRAFT_CONTROLS) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt': to_comfy_input(prompt), 'n': to_comfy_input(n),
            'strength': to_comfy_input(strength), 'seed': to_comfy_input(
            seed), 'recraft_style': to_comfy_input(recraft_style),
            'negative_prompt': to_comfy_input(negative_prompt),
            'recraft_controls': to_comfy_input(recraft_controls)},
            'class_type': 'RecraftImageToImageNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RecraftImageInpaintingNode(self, image: IMAGE, mask: MASK, prompt:
        str, n: int, seed: int, recraft_style: RECRAFT_V3_STYLE,
        negative_prompt: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'mask': to_comfy_input(mask), 'prompt': to_comfy_input(prompt),
            'n': to_comfy_input(n), 'seed': to_comfy_input(seed),
            'recraft_style': to_comfy_input(recraft_style),
            'negative_prompt': to_comfy_input(negative_prompt)},
            'class_type': 'RecraftImageInpaintingNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RecraftTextToVectorNode(self, prompt: str, substyle: str, size: str,
        n: int, seed: int, negative_prompt: str, recraft_controls:
        RECRAFT_CONTROLS) ->SVG:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'substyle': to_comfy_input(substyle), 'size': to_comfy_input(
            size), 'n': to_comfy_input(n), 'seed': to_comfy_input(seed),
            'negative_prompt': to_comfy_input(negative_prompt),
            'recraft_controls': to_comfy_input(recraft_controls)},
            'class_type': 'RecraftTextToVectorNode'}
        self._add_node(node_id, comfy_json_node)
        return SVG(node_id, 0)

    def RecraftVectorizeImageNode(self, image: IMAGE) ->SVG:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'RecraftVectorizeImageNode'}
        self._add_node(node_id, comfy_json_node)
        return SVG(node_id, 0)

    def RecraftRemoveBackgroundNode(self, image: IMAGE) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'RecraftRemoveBackgroundNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def RecraftReplaceBackgroundNode(self, image: IMAGE, prompt: str, n:
        int, seed: int, recraft_style: RECRAFT_V3_STYLE, negative_prompt: str
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt': to_comfy_input(prompt), 'n': to_comfy_input(n),
            'seed': to_comfy_input(seed), 'recraft_style': to_comfy_input(
            recraft_style), 'negative_prompt': to_comfy_input(
            negative_prompt)}, 'class_type': 'RecraftReplaceBackgroundNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RecraftCrispUpscaleNode(self, image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'RecraftCrispUpscaleNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RecraftCreativeUpscaleNode(self, image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'RecraftCreativeUpscaleNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RecraftStyleV3RealisticImage(self, substyle: str) ->RECRAFT_V3_STYLE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'substyle': to_comfy_input(substyle)},
            'class_type': 'RecraftStyleV3RealisticImage'}
        self._add_node(node_id, comfy_json_node)
        return RECRAFT_V3_STYLE(node_id, 0)

    def RecraftStyleV3DigitalIllustration(self, substyle: str
        ) ->RECRAFT_V3_STYLE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'substyle': to_comfy_input(substyle)},
            'class_type': 'RecraftStyleV3DigitalIllustration'}
        self._add_node(node_id, comfy_json_node)
        return RECRAFT_V3_STYLE(node_id, 0)

    def RecraftStyleV3LogoRaster(self, substyle: str) ->RECRAFT_V3_STYLE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'substyle': to_comfy_input(substyle)},
            'class_type': 'RecraftStyleV3LogoRaster'}
        self._add_node(node_id, comfy_json_node)
        return RECRAFT_V3_STYLE(node_id, 0)

    def RecraftStyleV3InfiniteStyleLibrary(self, style_id: str
        ) ->RECRAFT_V3_STYLE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'style_id': to_comfy_input(style_id)},
            'class_type': 'RecraftStyleV3InfiniteStyleLibrary'}
        self._add_node(node_id, comfy_json_node)
        return RECRAFT_V3_STYLE(node_id, 0)

    def RecraftColorRGB(self, r: int, g: int, b: int, recraft_color:
        RECRAFT_COLOR) ->RECRAFT_COLOR:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'r': to_comfy_input(r), 'g':
            to_comfy_input(g), 'b': to_comfy_input(b), 'recraft_color':
            to_comfy_input(recraft_color)}, 'class_type': 'RecraftColorRGB'}
        self._add_node(node_id, comfy_json_node)
        return RECRAFT_COLOR(node_id, 0)

    def RecraftControls(self, colors: RECRAFT_COLOR, background_color:
        RECRAFT_COLOR) ->RECRAFT_CONTROLS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'colors': to_comfy_input(colors),
            'background_color': to_comfy_input(background_color)},
            'class_type': 'RecraftControls'}
        self._add_node(node_id, comfy_json_node)
        return RECRAFT_CONTROLS(node_id, 0)

    def PixverseTextToVideoNode(self, prompt: str, aspect_ratio: str,
        quality: str, duration_seconds: str, motion_mode: str, seed: int,
        negative_prompt: str, pixverse_template: PIXVERSE_TEMPLATE) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'aspect_ratio': to_comfy_input(aspect_ratio), 'quality':
            to_comfy_input(quality), 'duration_seconds': to_comfy_input(
            duration_seconds), 'motion_mode': to_comfy_input(motion_mode),
            'seed': to_comfy_input(seed), 'negative_prompt': to_comfy_input
            (negative_prompt), 'pixverse_template': to_comfy_input(
            pixverse_template)}, 'class_type': 'PixverseTextToVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def PixverseImageToVideoNode(self, image: IMAGE, prompt: str, quality:
        str, duration_seconds: str, motion_mode: str, seed: int,
        negative_prompt: str, pixverse_template: PIXVERSE_TEMPLATE) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt': to_comfy_input(prompt), 'quality': to_comfy_input(
            quality), 'duration_seconds': to_comfy_input(duration_seconds),
            'motion_mode': to_comfy_input(motion_mode), 'seed':
            to_comfy_input(seed), 'negative_prompt': to_comfy_input(
            negative_prompt), 'pixverse_template': to_comfy_input(
            pixverse_template)}, 'class_type': 'PixverseImageToVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def PixverseTransitionVideoNode(self, first_frame: IMAGE, last_frame:
        IMAGE, prompt: str, quality: str, duration_seconds: str,
        motion_mode: str, seed: int, negative_prompt: str) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'first_frame': to_comfy_input(
            first_frame), 'last_frame': to_comfy_input(last_frame),
            'prompt': to_comfy_input(prompt), 'quality': to_comfy_input(
            quality), 'duration_seconds': to_comfy_input(duration_seconds),
            'motion_mode': to_comfy_input(motion_mode), 'seed':
            to_comfy_input(seed), 'negative_prompt': to_comfy_input(
            negative_prompt)}, 'class_type': 'PixverseTransitionVideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def PixverseTemplateNode(self, template: str) ->PIXVERSE_TEMPLATE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'template': to_comfy_input(template)},
            'class_type': 'PixverseTemplateNode'}
        self._add_node(node_id, comfy_json_node)
        return PIXVERSE_TEMPLATE(node_id, 0)

    def StabilityStableImageUltraNode(self, prompt: str, aspect_ratio: str,
        style_preset: str, seed: int, image: IMAGE, negative_prompt: str,
        image_denoise: float) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'aspect_ratio': to_comfy_input(aspect_ratio), 'style_preset':
            to_comfy_input(style_preset), 'seed': to_comfy_input(seed),
            'image': to_comfy_input(image), 'negative_prompt':
            to_comfy_input(negative_prompt), 'image_denoise':
            to_comfy_input(image_denoise)}, 'class_type':
            'StabilityStableImageUltraNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def StabilityStableImageSD_3_5Node(self, prompt: str, model: str,
        aspect_ratio: str, style_preset: str, cfg_scale: float, seed: int,
        image: IMAGE, negative_prompt: str, image_denoise: float) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'model': to_comfy_input(model), 'aspect_ratio': to_comfy_input(
            aspect_ratio), 'style_preset': to_comfy_input(style_preset),
            'cfg_scale': to_comfy_input(cfg_scale), 'seed': to_comfy_input(
            seed), 'image': to_comfy_input(image), 'negative_prompt':
            to_comfy_input(negative_prompt), 'image_denoise':
            to_comfy_input(image_denoise)}, 'class_type':
            'StabilityStableImageSD_3_5Node'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def StabilityUpscaleConservativeNode(self, image: IMAGE, prompt: str,
        creativity: float, seed: int, negative_prompt: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt': to_comfy_input(prompt), 'creativity': to_comfy_input(
            creativity), 'seed': to_comfy_input(seed), 'negative_prompt':
            to_comfy_input(negative_prompt)}, 'class_type':
            'StabilityUpscaleConservativeNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def StabilityUpscaleCreativeNode(self, image: IMAGE, prompt: str,
        creativity: float, style_preset: str, seed: int, negative_prompt: str
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt': to_comfy_input(prompt), 'creativity': to_comfy_input(
            creativity), 'style_preset': to_comfy_input(style_preset),
            'seed': to_comfy_input(seed), 'negative_prompt': to_comfy_input
            (negative_prompt)}, 'class_type': 'StabilityUpscaleCreativeNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def StabilityUpscaleFastNode(self, image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'StabilityUpscaleFastNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def PikaImageToVideoNode2_2(self, image: IMAGE, prompt_text: str,
        negative_prompt: str, seed: int, resolution: COMBO, duration: COMBO
        ) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'prompt_text': to_comfy_input(prompt_text), 'negative_prompt':
            to_comfy_input(negative_prompt), 'seed': to_comfy_input(seed),
            'resolution': to_comfy_input(resolution), 'duration':
            to_comfy_input(duration)}, 'class_type': 'PikaImageToVideoNode2_2'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def PikaTextToVideoNode2_2(self, prompt_text: str, negative_prompt: str,
        seed: int, resolution: COMBO, duration: COMBO, aspect_ratio: float
        ) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt_text': to_comfy_input(
            prompt_text), 'negative_prompt': to_comfy_input(negative_prompt
            ), 'seed': to_comfy_input(seed), 'resolution': to_comfy_input(
            resolution), 'duration': to_comfy_input(duration),
            'aspect_ratio': to_comfy_input(aspect_ratio)}, 'class_type':
            'PikaTextToVideoNode2_2'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def PikaScenesV2_2(self, prompt_text: str, negative_prompt: str, seed:
        int, resolution: COMBO, duration: COMBO, ingredients_mode: COMBO,
        aspect_ratio: float, image_ingredient_1: IMAGE, image_ingredient_2:
        IMAGE, image_ingredient_3: IMAGE, image_ingredient_4: IMAGE,
        image_ingredient_5: IMAGE) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt_text': to_comfy_input(
            prompt_text), 'negative_prompt': to_comfy_input(negative_prompt
            ), 'seed': to_comfy_input(seed), 'resolution': to_comfy_input(
            resolution), 'duration': to_comfy_input(duration),
            'ingredients_mode': to_comfy_input(ingredients_mode),
            'aspect_ratio': to_comfy_input(aspect_ratio),
            'image_ingredient_1': to_comfy_input(image_ingredient_1),
            'image_ingredient_2': to_comfy_input(image_ingredient_2),
            'image_ingredient_3': to_comfy_input(image_ingredient_3),
            'image_ingredient_4': to_comfy_input(image_ingredient_4),
            'image_ingredient_5': to_comfy_input(image_ingredient_5)},
            'class_type': 'PikaScenesV2_2'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def Pikadditions(self, video: VIDEO, image: IMAGE, prompt_text: str,
        negative_prompt: str, seed: int) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'video': to_comfy_input(video),
            'image': to_comfy_input(image), 'prompt_text': to_comfy_input(
            prompt_text), 'negative_prompt': to_comfy_input(negative_prompt
            ), 'seed': to_comfy_input(seed)}, 'class_type': 'Pikadditions'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def Pikaswaps(self, video: VIDEO, image: IMAGE, mask: MASK, prompt_text:
        str, negative_prompt: str, seed: int) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'video': to_comfy_input(video),
            'image': to_comfy_input(image), 'mask': to_comfy_input(mask),
            'prompt_text': to_comfy_input(prompt_text), 'negative_prompt':
            to_comfy_input(negative_prompt), 'seed': to_comfy_input(seed)},
            'class_type': 'Pikaswaps'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def Pikaffects(self, image: IMAGE, pikaffect: COMBO, prompt_text: str,
        negative_prompt: str, seed: int) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'pikaffect': to_comfy_input(pikaffect), 'prompt_text':
            to_comfy_input(prompt_text), 'negative_prompt': to_comfy_input(
            negative_prompt), 'seed': to_comfy_input(seed)}, 'class_type':
            'Pikaffects'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def PikaStartEndFrameNode2_2(self, image_start: IMAGE, image_end: IMAGE,
        prompt_text: str, negative_prompt: str, seed: int, resolution:
        COMBO, duration: COMBO) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image_start': to_comfy_input(
            image_start), 'image_end': to_comfy_input(image_end),
            'prompt_text': to_comfy_input(prompt_text), 'negative_prompt':
            to_comfy_input(negative_prompt), 'seed': to_comfy_input(seed),
            'resolution': to_comfy_input(resolution), 'duration':
            to_comfy_input(duration)}, 'class_type': 'PikaStartEndFrameNode2_2'
            }
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def RunwayFirstLastFrameNode(self, prompt: str, start_frame: IMAGE,
        end_frame: IMAGE, duration: COMBO, ratio: COMBO, seed: int) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'start_frame': to_comfy_input(start_frame), 'end_frame':
            to_comfy_input(end_frame), 'duration': to_comfy_input(duration),
            'ratio': to_comfy_input(ratio), 'seed': to_comfy_input(seed)},
            'class_type': 'RunwayFirstLastFrameNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def RunwayImageToVideoNodeGen3a(self, prompt: str, start_frame: IMAGE,
        duration: COMBO, ratio: COMBO, seed: int) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'start_frame': to_comfy_input(start_frame), 'duration':
            to_comfy_input(duration), 'ratio': to_comfy_input(ratio),
            'seed': to_comfy_input(seed)}, 'class_type':
            'RunwayImageToVideoNodeGen3a'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def RunwayImageToVideoNodeGen4(self, prompt: str, start_frame: IMAGE,
        duration: COMBO, ratio: COMBO, seed: int) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'start_frame': to_comfy_input(start_frame), 'duration':
            to_comfy_input(duration), 'ratio': to_comfy_input(ratio),
            'seed': to_comfy_input(seed)}, 'class_type':
            'RunwayImageToVideoNodeGen4'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def RunwayTextToImageNode(self, prompt: str, ratio: COMBO,
        reference_image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'ratio': to_comfy_input(ratio), 'reference_image':
            to_comfy_input(reference_image)}, 'class_type':
            'RunwayTextToImageNode'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def TripoTextToModelNode(self, prompt: str, negative_prompt: str,
        model_version: COMBO, style: COMBO, texture: bool, pbr: bool,
        image_seed: int, model_seed: int, texture_seed: int,
        texture_quality: str, face_limit: int, quad: bool) ->(StrNodeOutput,
        MODEL_TASK_ID):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt),
            'model_version': to_comfy_input(model_version), 'style':
            to_comfy_input(style), 'texture': to_comfy_input(texture),
            'pbr': to_comfy_input(pbr), 'image_seed': to_comfy_input(
            image_seed), 'model_seed': to_comfy_input(model_seed),
            'texture_seed': to_comfy_input(texture_seed), 'texture_quality':
            to_comfy_input(texture_quality), 'face_limit': to_comfy_input(
            face_limit), 'quad': to_comfy_input(quad)}, 'class_type':
            'TripoTextToModelNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), MODEL_TASK_ID(node_id, 1)

    def TripoImageToModelNode(self, image: IMAGE, model_version: COMBO,
        style: COMBO, texture: bool, pbr: bool, model_seed: int,
        orientation: COMBO, texture_seed: int, texture_quality: str,
        texture_alignment: str, face_limit: int, quad: bool) ->(StrNodeOutput,
        MODEL_TASK_ID):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'model_version': to_comfy_input(model_version), 'style':
            to_comfy_input(style), 'texture': to_comfy_input(texture),
            'pbr': to_comfy_input(pbr), 'model_seed': to_comfy_input(
            model_seed), 'orientation': to_comfy_input(orientation),
            'texture_seed': to_comfy_input(texture_seed), 'texture_quality':
            to_comfy_input(texture_quality), 'texture_alignment':
            to_comfy_input(texture_alignment), 'face_limit': to_comfy_input
            (face_limit), 'quad': to_comfy_input(quad)}, 'class_type':
            'TripoImageToModelNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), MODEL_TASK_ID(node_id, 1)

    def TripoMultiviewToModelNode(self, image: IMAGE, image_left: IMAGE,
        image_back: IMAGE, image_right: IMAGE, model_version: COMBO,
        orientation: COMBO, texture: bool, pbr: bool, model_seed: int,
        texture_seed: int, texture_quality: str, texture_alignment: str,
        face_limit: int, quad: bool) ->(StrNodeOutput, MODEL_TASK_ID):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'image_left': to_comfy_input(image_left), 'image_back':
            to_comfy_input(image_back), 'image_right': to_comfy_input(
            image_right), 'model_version': to_comfy_input(model_version),
            'orientation': to_comfy_input(orientation), 'texture':
            to_comfy_input(texture), 'pbr': to_comfy_input(pbr),
            'model_seed': to_comfy_input(model_seed), 'texture_seed':
            to_comfy_input(texture_seed), 'texture_quality': to_comfy_input
            (texture_quality), 'texture_alignment': to_comfy_input(
            texture_alignment), 'face_limit': to_comfy_input(face_limit),
            'quad': to_comfy_input(quad)}, 'class_type':
            'TripoMultiviewToModelNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), MODEL_TASK_ID(node_id, 1)

    def TripoTextureNode(self, model_task_id: MODEL_TASK_ID, texture: bool,
        pbr: bool, texture_seed: int, texture_quality: str,
        texture_alignment: str) ->(StrNodeOutput, MODEL_TASK_ID):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_task_id': to_comfy_input(
            model_task_id), 'texture': to_comfy_input(texture), 'pbr':
            to_comfy_input(pbr), 'texture_seed': to_comfy_input(
            texture_seed), 'texture_quality': to_comfy_input(
            texture_quality), 'texture_alignment': to_comfy_input(
            texture_alignment)}, 'class_type': 'TripoTextureNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), MODEL_TASK_ID(node_id, 1)

    def TripoRefineNode(self, model_task_id: MODEL_TASK_ID) ->(StrNodeOutput,
        MODEL_TASK_ID):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_task_id': to_comfy_input(
            model_task_id)}, 'class_type': 'TripoRefineNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), MODEL_TASK_ID(node_id, 1)

    def TripoRigNode(self, original_model_task_id: MODEL_TASK_ID) ->(
        StrNodeOutput, RIG_TASK_ID):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'original_model_task_id':
            to_comfy_input(original_model_task_id)}, 'class_type':
            'TripoRigNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), RIG_TASK_ID(node_id, 1)

    def TripoRetargetNode(self, original_model_task_id: RIG_TASK_ID,
        animation: str) ->(StrNodeOutput, RETARGET_TASK_ID):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'original_model_task_id':
            to_comfy_input(original_model_task_id), 'animation':
            to_comfy_input(animation)}, 'class_type': 'TripoRetargetNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), RETARGET_TASK_ID(node_id, 1)

    def TripoConversionNode(self, original_model_task_id:
        MODEL_TASK_ID_RIG_TASK_ID_RETARGET_TASK_ID, format: str, quad: bool,
        face_limit: int, texture_size: int, texture_format: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'original_model_task_id':
            to_comfy_input(original_model_task_id), 'format':
            to_comfy_input(format), 'quad': to_comfy_input(quad),
            'face_limit': to_comfy_input(face_limit), 'texture_size':
            to_comfy_input(texture_size), 'texture_format': to_comfy_input(
            texture_format)}, 'class_type': 'TripoConversionNode'}
        self._add_node(node_id, comfy_json_node)

    def MoonvalleyImg2VideoNode(self, prompt: str, negative_prompt: str,
        resolution: COMBO, prompt_adherence: float, seed: int, steps: int,
        image: IMAGE) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt),
            'resolution': to_comfy_input(resolution), 'prompt_adherence':
            to_comfy_input(prompt_adherence), 'seed': to_comfy_input(seed),
            'steps': to_comfy_input(steps), 'image': to_comfy_input(image)},
            'class_type': 'MoonvalleyImg2VideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def MoonvalleyTxt2VideoNode(self, prompt: str, negative_prompt: str,
        resolution: COMBO, prompt_adherence: float, seed: int, steps: int
        ) ->VIDEO:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'negative_prompt': to_comfy_input(negative_prompt),
            'resolution': to_comfy_input(resolution), 'prompt_adherence':
            to_comfy_input(prompt_adherence), 'seed': to_comfy_input(seed),
            'steps': to_comfy_input(steps)}, 'class_type':
            'MoonvalleyTxt2VideoNode'}
        self._add_node(node_id, comfy_json_node)
        return VIDEO(node_id, 0)

    def Rodin3D_Regular(self, Images: IMAGE, Seed: int, Material_Type:
        COMBO, Polygon_count: COMBO) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'Images': to_comfy_input(Images),
            'Seed': to_comfy_input(Seed), 'Material_Type': to_comfy_input(
            Material_Type), 'Polygon_count': to_comfy_input(Polygon_count)},
            'class_type': 'Rodin3D_Regular'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def Rodin3D_Detail(self, Images: IMAGE, Seed: int, Material_Type: COMBO,
        Polygon_count: COMBO) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'Images': to_comfy_input(Images),
            'Seed': to_comfy_input(Seed), 'Material_Type': to_comfy_input(
            Material_Type), 'Polygon_count': to_comfy_input(Polygon_count)},
            'class_type': 'Rodin3D_Detail'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def Rodin3D_Smooth(self, Images: IMAGE, Seed: int, Material_Type: COMBO,
        Polygon_count: COMBO) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'Images': to_comfy_input(Images),
            'Seed': to_comfy_input(Seed), 'Material_Type': to_comfy_input(
            Material_Type), 'Polygon_count': to_comfy_input(Polygon_count)},
            'class_type': 'Rodin3D_Smooth'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def Rodin3D_Sketch(self, Images: IMAGE, Seed: int) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'Images': to_comfy_input(Images),
            'Seed': to_comfy_input(Seed)}, 'class_type': 'Rodin3D_Sketch'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def GeminiNode(self, prompt: str, model: COMBO, seed: int, images:
        IMAGE, audio: AUDIO, video: VIDEO, files: GEMINI_INPUT_FILES
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'model': to_comfy_input(model), 'seed': to_comfy_input(seed),
            'images': to_comfy_input(images), 'audio': to_comfy_input(audio
            ), 'video': to_comfy_input(video), 'files': to_comfy_input(
            files)}, 'class_type': 'GeminiNode'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def GeminiInputFiles(self, file: COMBO, GEMINI_INPUT_FILES:
        GEMINI_INPUT_FILES) ->GEMINI_INPUT_FILES:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'file': to_comfy_input(file),
            'GEMINI_INPUT_FILES': to_comfy_input(GEMINI_INPUT_FILES)},
            'class_type': 'GeminiInputFiles'}
        self._add_node(node_id, comfy_json_node)
        return GEMINI_INPUT_FILES(node_id, 0)

    def SaveImageWebsocket(self, images: IMAGE) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images)},
            'class_type': 'SaveImageWebsocket'}
        self._add_node(node_id, comfy_json_node)

    def UltralyticsDetectorProvider(self, model_name: str) ->(BBOX_DETECTOR,
        SEGM_DETECTOR):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_name': to_comfy_input(
            model_name)}, 'class_type': 'UltralyticsDetectorProvider'}
        self._add_node(node_id, comfy_json_node)
        return BBOX_DETECTOR(node_id, 0), SEGM_DETECTOR(node_id, 1)

    def UltimateSDUpscale(self, image: IMAGE, model: MODEL, positive:
        CONDITIONING, negative: CONDITIONING, vae: VAE, upscale_by: float,
        seed: int, steps: int, cfg: float, sampler_name: str, scheduler:
        str, denoise: float, upscale_model: UPSCALE_MODEL, mode_type: str,
        tile_width: int, tile_height: int, mask_blur: int, tile_padding:
        int, seam_fix_mode: str, seam_fix_denoise: float, seam_fix_width:
        int, seam_fix_mask_blur: int, seam_fix_padding: int,
        force_uniform_tiles: bool, tiled_decode: bool) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'model': to_comfy_input(model), 'positive': to_comfy_input(
            positive), 'negative': to_comfy_input(negative), 'vae':
            to_comfy_input(vae), 'upscale_by': to_comfy_input(upscale_by),
            'seed': to_comfy_input(seed), 'steps': to_comfy_input(steps),
            'cfg': to_comfy_input(cfg), 'sampler_name': to_comfy_input(
            sampler_name), 'scheduler': to_comfy_input(scheduler),
            'denoise': to_comfy_input(denoise), 'upscale_model':
            to_comfy_input(upscale_model), 'mode_type': to_comfy_input(
            mode_type), 'tile_width': to_comfy_input(tile_width),
            'tile_height': to_comfy_input(tile_height), 'mask_blur':
            to_comfy_input(mask_blur), 'tile_padding': to_comfy_input(
            tile_padding), 'seam_fix_mode': to_comfy_input(seam_fix_mode),
            'seam_fix_denoise': to_comfy_input(seam_fix_denoise),
            'seam_fix_width': to_comfy_input(seam_fix_width),
            'seam_fix_mask_blur': to_comfy_input(seam_fix_mask_blur),
            'seam_fix_padding': to_comfy_input(seam_fix_padding),
            'force_uniform_tiles': to_comfy_input(force_uniform_tiles),
            'tiled_decode': to_comfy_input(tiled_decode)}, 'class_type':
            'UltimateSDUpscale'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def UltimateSDUpscaleNoUpscale(self, upscaled_image: IMAGE, model:
        MODEL, positive: CONDITIONING, negative: CONDITIONING, vae: VAE,
        seed: int, steps: int, cfg: float, sampler_name: str, scheduler:
        str, denoise: float, mode_type: str, tile_width: int, tile_height:
        int, mask_blur: int, tile_padding: int, seam_fix_mode: str,
        seam_fix_denoise: float, seam_fix_width: int, seam_fix_mask_blur:
        int, seam_fix_padding: int, force_uniform_tiles: bool, tiled_decode:
        bool) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'upscaled_image': to_comfy_input(
            upscaled_image), 'model': to_comfy_input(model), 'positive':
            to_comfy_input(positive), 'negative': to_comfy_input(negative),
            'vae': to_comfy_input(vae), 'seed': to_comfy_input(seed),
            'steps': to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'mode_type': to_comfy_input(mode_type), 'tile_width':
            to_comfy_input(tile_width), 'tile_height': to_comfy_input(
            tile_height), 'mask_blur': to_comfy_input(mask_blur),
            'tile_padding': to_comfy_input(tile_padding), 'seam_fix_mode':
            to_comfy_input(seam_fix_mode), 'seam_fix_denoise':
            to_comfy_input(seam_fix_denoise), 'seam_fix_width':
            to_comfy_input(seam_fix_width), 'seam_fix_mask_blur':
            to_comfy_input(seam_fix_mask_blur), 'seam_fix_padding':
            to_comfy_input(seam_fix_padding), 'force_uniform_tiles':
            to_comfy_input(force_uniform_tiles), 'tiled_decode':
            to_comfy_input(tiled_decode)}, 'class_type':
            'UltimateSDUpscaleNoUpscale'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def UltimateSDUpscaleCustomSample(self, image: IMAGE, model: MODEL,
        positive: CONDITIONING, negative: CONDITIONING, vae: VAE,
        upscale_by: float, seed: int, steps: int, cfg: float, sampler_name:
        str, scheduler: str, denoise: float, mode_type: str, tile_width:
        int, tile_height: int, mask_blur: int, tile_padding: int,
        seam_fix_mode: str, seam_fix_denoise: float, seam_fix_width: int,
        seam_fix_mask_blur: int, seam_fix_padding: int, force_uniform_tiles:
        bool, tiled_decode: bool, upscale_model: UPSCALE_MODEL,
        custom_sampler: SAMPLER, custom_sigmas: SIGMAS) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'model': to_comfy_input(model), 'positive': to_comfy_input(
            positive), 'negative': to_comfy_input(negative), 'vae':
            to_comfy_input(vae), 'upscale_by': to_comfy_input(upscale_by),
            'seed': to_comfy_input(seed), 'steps': to_comfy_input(steps),
            'cfg': to_comfy_input(cfg), 'sampler_name': to_comfy_input(
            sampler_name), 'scheduler': to_comfy_input(scheduler),
            'denoise': to_comfy_input(denoise), 'mode_type': to_comfy_input
            (mode_type), 'tile_width': to_comfy_input(tile_width),
            'tile_height': to_comfy_input(tile_height), 'mask_blur':
            to_comfy_input(mask_blur), 'tile_padding': to_comfy_input(
            tile_padding), 'seam_fix_mode': to_comfy_input(seam_fix_mode),
            'seam_fix_denoise': to_comfy_input(seam_fix_denoise),
            'seam_fix_width': to_comfy_input(seam_fix_width),
            'seam_fix_mask_blur': to_comfy_input(seam_fix_mask_blur),
            'seam_fix_padding': to_comfy_input(seam_fix_padding),
            'force_uniform_tiles': to_comfy_input(force_uniform_tiles),
            'tiled_decode': to_comfy_input(tiled_decode), 'upscale_model':
            to_comfy_input(upscale_model), 'custom_sampler': to_comfy_input
            (custom_sampler), 'custom_sigmas': to_comfy_input(custom_sigmas
            )}, 'class_type': 'UltimateSDUpscaleCustomSample'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SAMLoader(self, model_name: str, device_mode: str) ->SAM_MODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_name': to_comfy_input(
            model_name), 'device_mode': to_comfy_input(device_mode)},
            'class_type': 'SAMLoader'}
        self._add_node(node_id, comfy_json_node)
        return SAM_MODEL(node_id, 0)

    def CLIPSegDetectorProvider(self, text: str, blur: float, threshold:
        float, dilation_factor: int) ->BBOX_DETECTOR:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'text': to_comfy_input(text), 'blur':
            to_comfy_input(blur), 'threshold': to_comfy_input(threshold),
            'dilation_factor': to_comfy_input(dilation_factor)},
            'class_type': 'CLIPSegDetectorProvider'}
        self._add_node(node_id, comfy_json_node)
        return BBOX_DETECTOR(node_id, 0)

    def ONNXDetectorProvider(self, model_name: str) ->BBOX_DETECTOR:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model_name': to_comfy_input(
            model_name)}, 'class_type': 'ONNXDetectorProvider'}
        self._add_node(node_id, comfy_json_node)
        return BBOX_DETECTOR(node_id, 0)

    def BitwiseAndMaskForEach(self, base_segs: SEGS, mask_segs: SEGS) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'base_segs': to_comfy_input(base_segs
            ), 'mask_segs': to_comfy_input(mask_segs)}, 'class_type':
            'BitwiseAndMaskForEach'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def SubtractMaskForEach(self, base_segs: SEGS, mask_segs: SEGS) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'base_segs': to_comfy_input(base_segs
            ), 'mask_segs': to_comfy_input(mask_segs)}, 'class_type':
            'SubtractMaskForEach'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def DetailerForEach(self, image: IMAGE, segs: SEGS, model: MODEL, clip:
        CLIP, vae: VAE, guide_size: float, guide_size_for: bool, max_size:
        float, seed: int, steps: int, cfg: float, sampler_name: str,
        scheduler: str, positive: CONDITIONING, negative: CONDITIONING,
        denoise: float, feather: int, noise_mask: bool, force_inpaint: bool,
        wildcard: str, cycle: int, detailer_hook: DETAILER_HOOK,
        inpaint_model: bool, noise_mask_feather: int, scheduler_func_opt:
        SCHEDULER_FUNC, tiled_encode: bool, tiled_decode: bool) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'vae': to_comfy_input(vae),
            'guide_size': to_comfy_input(guide_size), 'guide_size_for':
            to_comfy_input(guide_size_for), 'max_size': to_comfy_input(
            max_size), 'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'denoise': to_comfy_input
            (denoise), 'feather': to_comfy_input(feather), 'noise_mask':
            to_comfy_input(noise_mask), 'force_inpaint': to_comfy_input(
            force_inpaint), 'wildcard': to_comfy_input(wildcard), 'cycle':
            to_comfy_input(cycle), 'detailer_hook': to_comfy_input(
            detailer_hook), 'inpaint_model': to_comfy_input(inpaint_model),
            'noise_mask_feather': to_comfy_input(noise_mask_feather),
            'scheduler_func_opt': to_comfy_input(scheduler_func_opt),
            'tiled_encode': to_comfy_input(tiled_encode), 'tiled_decode':
            to_comfy_input(tiled_decode)}, 'class_type': 'DetailerForEach'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DetailerForEachAutoRetry(self, image: IMAGE, segs: SEGS, model:
        MODEL, clip: CLIP, vae: VAE, guide_size: float, guide_size_for:
        bool, max_size: float, seed: int, steps: int, cfg: float,
        sampler_name: str, scheduler: str, positive: CONDITIONING, negative:
        CONDITIONING, denoise: float, feather: int, noise_mask: bool,
        force_inpaint: bool, wildcard: str, cycle: int, max_retries: int,
        detailer_hook: DETAILER_HOOK, inpaint_model: bool,
        noise_mask_feather: int, scheduler_func_opt: SCHEDULER_FUNC,
        tiled_encode: bool, tiled_decode: bool) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'vae': to_comfy_input(vae),
            'guide_size': to_comfy_input(guide_size), 'guide_size_for':
            to_comfy_input(guide_size_for), 'max_size': to_comfy_input(
            max_size), 'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'denoise': to_comfy_input
            (denoise), 'feather': to_comfy_input(feather), 'noise_mask':
            to_comfy_input(noise_mask), 'force_inpaint': to_comfy_input(
            force_inpaint), 'wildcard': to_comfy_input(wildcard), 'cycle':
            to_comfy_input(cycle), 'max_retries': to_comfy_input(
            max_retries), 'detailer_hook': to_comfy_input(detailer_hook),
            'inpaint_model': to_comfy_input(inpaint_model),
            'noise_mask_feather': to_comfy_input(noise_mask_feather),
            'scheduler_func_opt': to_comfy_input(scheduler_func_opt),
            'tiled_encode': to_comfy_input(tiled_encode), 'tiled_decode':
            to_comfy_input(tiled_decode)}, 'class_type':
            'DetailerForEachAutoRetry'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DetailerForEachDebug(self, image: IMAGE, segs: SEGS, model: MODEL,
        clip: CLIP, vae: VAE, guide_size: float, guide_size_for: bool,
        max_size: float, seed: int, steps: int, cfg: float, sampler_name:
        str, scheduler: str, positive: CONDITIONING, negative: CONDITIONING,
        denoise: float, feather: int, noise_mask: bool, force_inpaint: bool,
        wildcard: str, cycle: int, detailer_hook: DETAILER_HOOK,
        inpaint_model: bool, noise_mask_feather: int, scheduler_func_opt:
        SCHEDULER_FUNC, tiled_encode: bool, tiled_decode: bool) ->(IMAGE,
        IMAGE, IMAGE, IMAGE, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'vae': to_comfy_input(vae),
            'guide_size': to_comfy_input(guide_size), 'guide_size_for':
            to_comfy_input(guide_size_for), 'max_size': to_comfy_input(
            max_size), 'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'denoise': to_comfy_input
            (denoise), 'feather': to_comfy_input(feather), 'noise_mask':
            to_comfy_input(noise_mask), 'force_inpaint': to_comfy_input(
            force_inpaint), 'wildcard': to_comfy_input(wildcard), 'cycle':
            to_comfy_input(cycle), 'detailer_hook': to_comfy_input(
            detailer_hook), 'inpaint_model': to_comfy_input(inpaint_model),
            'noise_mask_feather': to_comfy_input(noise_mask_feather),
            'scheduler_func_opt': to_comfy_input(scheduler_func_opt),
            'tiled_encode': to_comfy_input(tiled_encode), 'tiled_decode':
            to_comfy_input(tiled_decode)}, 'class_type': 'DetailerForEachDebug'
            }
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), IMAGE(node_id, 1), IMAGE(node_id, 2), IMAGE(
            node_id, 3), IMAGE(node_id, 4)

    def DetailerForEachPipe(self, image: IMAGE, segs: SEGS, guide_size:
        float, guide_size_for: bool, max_size: float, seed: int, steps: int,
        cfg: float, sampler_name: str, scheduler: str, denoise: float,
        feather: int, noise_mask: bool, force_inpaint: bool, basic_pipe:
        BASIC_PIPE, wildcard: str, refiner_ratio: float, cycle: int,
        detailer_hook: DETAILER_HOOK, refiner_basic_pipe_opt: BASIC_PIPE,
        inpaint_model: bool, noise_mask_feather: int, scheduler_func_opt:
        SCHEDULER_FUNC, tiled_encode: bool, tiled_decode: bool) ->(IMAGE,
        SEGS, BASIC_PIPE, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'guide_size': to_comfy_input(
            guide_size), 'guide_size_for': to_comfy_input(guide_size_for),
            'max_size': to_comfy_input(max_size), 'seed': to_comfy_input(
            seed), 'steps': to_comfy_input(steps), 'cfg': to_comfy_input(
            cfg), 'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'feather': to_comfy_input(feather), 'noise_mask':
            to_comfy_input(noise_mask), 'force_inpaint': to_comfy_input(
            force_inpaint), 'basic_pipe': to_comfy_input(basic_pipe),
            'wildcard': to_comfy_input(wildcard), 'refiner_ratio':
            to_comfy_input(refiner_ratio), 'cycle': to_comfy_input(cycle),
            'detailer_hook': to_comfy_input(detailer_hook),
            'refiner_basic_pipe_opt': to_comfy_input(refiner_basic_pipe_opt
            ), 'inpaint_model': to_comfy_input(inpaint_model),
            'noise_mask_feather': to_comfy_input(noise_mask_feather),
            'scheduler_func_opt': to_comfy_input(scheduler_func_opt),
            'tiled_encode': to_comfy_input(tiled_encode), 'tiled_decode':
            to_comfy_input(tiled_decode)}, 'class_type': 'DetailerForEachPipe'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), SEGS(node_id, 1), BASIC_PIPE(node_id, 2
            ), IMAGE(node_id, 3)

    def DetailerForEachDebugPipe(self, image: IMAGE, segs: SEGS, guide_size:
        float, guide_size_for: bool, max_size: float, seed: int, steps: int,
        cfg: float, sampler_name: str, scheduler: str, denoise: float,
        feather: int, noise_mask: bool, force_inpaint: bool, basic_pipe:
        BASIC_PIPE, wildcard: str, refiner_ratio: float, cycle: int,
        detailer_hook: DETAILER_HOOK, refiner_basic_pipe_opt: BASIC_PIPE,
        inpaint_model: bool, noise_mask_feather: int, scheduler_func_opt:
        SCHEDULER_FUNC, tiled_encode: bool, tiled_decode: bool) ->(IMAGE,
        SEGS, BASIC_PIPE, IMAGE, IMAGE, IMAGE, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'guide_size': to_comfy_input(
            guide_size), 'guide_size_for': to_comfy_input(guide_size_for),
            'max_size': to_comfy_input(max_size), 'seed': to_comfy_input(
            seed), 'steps': to_comfy_input(steps), 'cfg': to_comfy_input(
            cfg), 'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'feather': to_comfy_input(feather), 'noise_mask':
            to_comfy_input(noise_mask), 'force_inpaint': to_comfy_input(
            force_inpaint), 'basic_pipe': to_comfy_input(basic_pipe),
            'wildcard': to_comfy_input(wildcard), 'refiner_ratio':
            to_comfy_input(refiner_ratio), 'cycle': to_comfy_input(cycle),
            'detailer_hook': to_comfy_input(detailer_hook),
            'refiner_basic_pipe_opt': to_comfy_input(refiner_basic_pipe_opt
            ), 'inpaint_model': to_comfy_input(inpaint_model),
            'noise_mask_feather': to_comfy_input(noise_mask_feather),
            'scheduler_func_opt': to_comfy_input(scheduler_func_opt),
            'tiled_encode': to_comfy_input(tiled_encode), 'tiled_decode':
            to_comfy_input(tiled_decode)}, 'class_type':
            'DetailerForEachDebugPipe'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), SEGS(node_id, 1), BASIC_PIPE(node_id, 2
            ), IMAGE(node_id, 3), IMAGE(node_id, 4), IMAGE(node_id, 5), IMAGE(
            node_id, 6)

    def DetailerForEachPipeForAnimateDiff(self, image_frames: IMAGE, segs:
        SEGS, guide_size: float, guide_size_for: bool, max_size: float,
        seed: int, steps: int, cfg: float, sampler_name: str, scheduler:
        str, denoise: float, feather: int, basic_pipe: BASIC_PIPE,
        refiner_ratio: float, detailer_hook: DETAILER_HOOK,
        refiner_basic_pipe_opt: BASIC_PIPE, noise_mask_feather: int,
        scheduler_func_opt: SCHEDULER_FUNC) ->(IMAGE, SEGS, BASIC_PIPE, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image_frames': to_comfy_input(
            image_frames), 'segs': to_comfy_input(segs), 'guide_size':
            to_comfy_input(guide_size), 'guide_size_for': to_comfy_input(
            guide_size_for), 'max_size': to_comfy_input(max_size), 'seed':
            to_comfy_input(seed), 'steps': to_comfy_input(steps), 'cfg':
            to_comfy_input(cfg), 'sampler_name': to_comfy_input(
            sampler_name), 'scheduler': to_comfy_input(scheduler),
            'denoise': to_comfy_input(denoise), 'feather': to_comfy_input(
            feather), 'basic_pipe': to_comfy_input(basic_pipe),
            'refiner_ratio': to_comfy_input(refiner_ratio), 'detailer_hook':
            to_comfy_input(detailer_hook), 'refiner_basic_pipe_opt':
            to_comfy_input(refiner_basic_pipe_opt), 'noise_mask_feather':
            to_comfy_input(noise_mask_feather), 'scheduler_func_opt':
            to_comfy_input(scheduler_func_opt)}, 'class_type':
            'DetailerForEachPipeForAnimateDiff'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), SEGS(node_id, 1), BASIC_PIPE(node_id, 2
            ), IMAGE(node_id, 3)

    def SAMDetectorCombined(self, sam_model: SAM_MODEL, segs: SEGS, image:
        IMAGE, detection_hint: str, dilation: int, threshold: float,
        bbox_expansion: int, mask_hint_threshold: float,
        mask_hint_use_negative: str) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sam_model': to_comfy_input(sam_model
            ), 'segs': to_comfy_input(segs), 'image': to_comfy_input(image),
            'detection_hint': to_comfy_input(detection_hint), 'dilation':
            to_comfy_input(dilation), 'threshold': to_comfy_input(threshold
            ), 'bbox_expansion': to_comfy_input(bbox_expansion),
            'mask_hint_threshold': to_comfy_input(mask_hint_threshold),
            'mask_hint_use_negative': to_comfy_input(mask_hint_use_negative
            )}, 'class_type': 'SAMDetectorCombined'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def SAMDetectorSegmented(self, sam_model: SAM_MODEL, segs: SEGS, image:
        IMAGE, detection_hint: str, dilation: int, threshold: float,
        bbox_expansion: int, mask_hint_threshold: float,
        mask_hint_use_negative: str) ->(MASK, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sam_model': to_comfy_input(sam_model
            ), 'segs': to_comfy_input(segs), 'image': to_comfy_input(image),
            'detection_hint': to_comfy_input(detection_hint), 'dilation':
            to_comfy_input(dilation), 'threshold': to_comfy_input(threshold
            ), 'bbox_expansion': to_comfy_input(bbox_expansion),
            'mask_hint_threshold': to_comfy_input(mask_hint_threshold),
            'mask_hint_use_negative': to_comfy_input(mask_hint_use_negative
            )}, 'class_type': 'SAMDetectorSegmented'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0), MASK(node_id, 1)

    def FaceDetailer(self, image: IMAGE, model: MODEL, clip: CLIP, vae: VAE,
        guide_size: float, guide_size_for: bool, max_size: float, seed: int,
        steps: int, cfg: float, sampler_name: str, scheduler: str, positive:
        CONDITIONING, negative: CONDITIONING, denoise: float, feather: int,
        noise_mask: bool, force_inpaint: bool, bbox_threshold: float,
        bbox_dilation: int, bbox_crop_factor: float, sam_detection_hint:
        str, sam_dilation: int, sam_threshold: float, sam_bbox_expansion:
        int, sam_mask_hint_threshold: float, sam_mask_hint_use_negative:
        str, drop_size: int, bbox_detector: BBOX_DETECTOR, wildcard: str,
        cycle: int, sam_model_opt: SAM_MODEL, segm_detector_opt:
        SEGM_DETECTOR, detailer_hook: DETAILER_HOOK, inpaint_model: bool,
        noise_mask_feather: int, scheduler_func_opt: SCHEDULER_FUNC,
        tiled_encode: bool, tiled_decode: bool) ->(IMAGE, IMAGE, IMAGE,
        MASK, DETAILER_PIPE, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'model': to_comfy_input(model), 'clip': to_comfy_input(clip),
            'vae': to_comfy_input(vae), 'guide_size': to_comfy_input(
            guide_size), 'guide_size_for': to_comfy_input(guide_size_for),
            'max_size': to_comfy_input(max_size), 'seed': to_comfy_input(
            seed), 'steps': to_comfy_input(steps), 'cfg': to_comfy_input(
            cfg), 'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'denoise': to_comfy_input
            (denoise), 'feather': to_comfy_input(feather), 'noise_mask':
            to_comfy_input(noise_mask), 'force_inpaint': to_comfy_input(
            force_inpaint), 'bbox_threshold': to_comfy_input(bbox_threshold
            ), 'bbox_dilation': to_comfy_input(bbox_dilation),
            'bbox_crop_factor': to_comfy_input(bbox_crop_factor),
            'sam_detection_hint': to_comfy_input(sam_detection_hint),
            'sam_dilation': to_comfy_input(sam_dilation), 'sam_threshold':
            to_comfy_input(sam_threshold), 'sam_bbox_expansion':
            to_comfy_input(sam_bbox_expansion), 'sam_mask_hint_threshold':
            to_comfy_input(sam_mask_hint_threshold),
            'sam_mask_hint_use_negative': to_comfy_input(
            sam_mask_hint_use_negative), 'drop_size': to_comfy_input(
            drop_size), 'bbox_detector': to_comfy_input(bbox_detector),
            'wildcard': to_comfy_input(wildcard), 'cycle': to_comfy_input(
            cycle), 'sam_model_opt': to_comfy_input(sam_model_opt),
            'segm_detector_opt': to_comfy_input(segm_detector_opt),
            'detailer_hook': to_comfy_input(detailer_hook), 'inpaint_model':
            to_comfy_input(inpaint_model), 'noise_mask_feather':
            to_comfy_input(noise_mask_feather), 'scheduler_func_opt':
            to_comfy_input(scheduler_func_opt), 'tiled_encode':
            to_comfy_input(tiled_encode), 'tiled_decode': to_comfy_input(
            tiled_decode)}, 'class_type': 'FaceDetailer'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), IMAGE(node_id, 1), IMAGE(node_id, 2), MASK(
            node_id, 3), DETAILER_PIPE(node_id, 4), IMAGE(node_id, 5)

    def FaceDetailerPipe(self, image: IMAGE, detailer_pipe: DETAILER_PIPE,
        guide_size: float, guide_size_for: bool, max_size: float, seed: int,
        steps: int, cfg: float, sampler_name: str, scheduler: str, denoise:
        float, feather: int, noise_mask: bool, force_inpaint: bool,
        bbox_threshold: float, bbox_dilation: int, bbox_crop_factor: float,
        sam_detection_hint: str, sam_dilation: int, sam_threshold: float,
        sam_bbox_expansion: int, sam_mask_hint_threshold: float,
        sam_mask_hint_use_negative: str, drop_size: int, refiner_ratio:
        float, cycle: int, inpaint_model: bool, noise_mask_feather: int,
        scheduler_func_opt: SCHEDULER_FUNC, tiled_encode: bool,
        tiled_decode: bool) ->(IMAGE, IMAGE, IMAGE, MASK, DETAILER_PIPE, IMAGE
        ):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'detailer_pipe': to_comfy_input(detailer_pipe), 'guide_size':
            to_comfy_input(guide_size), 'guide_size_for': to_comfy_input(
            guide_size_for), 'max_size': to_comfy_input(max_size), 'seed':
            to_comfy_input(seed), 'steps': to_comfy_input(steps), 'cfg':
            to_comfy_input(cfg), 'sampler_name': to_comfy_input(
            sampler_name), 'scheduler': to_comfy_input(scheduler),
            'denoise': to_comfy_input(denoise), 'feather': to_comfy_input(
            feather), 'noise_mask': to_comfy_input(noise_mask),
            'force_inpaint': to_comfy_input(force_inpaint),
            'bbox_threshold': to_comfy_input(bbox_threshold),
            'bbox_dilation': to_comfy_input(bbox_dilation),
            'bbox_crop_factor': to_comfy_input(bbox_crop_factor),
            'sam_detection_hint': to_comfy_input(sam_detection_hint),
            'sam_dilation': to_comfy_input(sam_dilation), 'sam_threshold':
            to_comfy_input(sam_threshold), 'sam_bbox_expansion':
            to_comfy_input(sam_bbox_expansion), 'sam_mask_hint_threshold':
            to_comfy_input(sam_mask_hint_threshold),
            'sam_mask_hint_use_negative': to_comfy_input(
            sam_mask_hint_use_negative), 'drop_size': to_comfy_input(
            drop_size), 'refiner_ratio': to_comfy_input(refiner_ratio),
            'cycle': to_comfy_input(cycle), 'inpaint_model': to_comfy_input
            (inpaint_model), 'noise_mask_feather': to_comfy_input(
            noise_mask_feather), 'scheduler_func_opt': to_comfy_input(
            scheduler_func_opt), 'tiled_encode': to_comfy_input(
            tiled_encode), 'tiled_decode': to_comfy_input(tiled_decode)},
            'class_type': 'FaceDetailerPipe'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), IMAGE(node_id, 1), IMAGE(node_id, 2), MASK(
            node_id, 3), DETAILER_PIPE(node_id, 4), IMAGE(node_id, 5)

    def MaskDetailerPipe(self, image: IMAGE, mask: MASK, basic_pipe:
        BASIC_PIPE, guide_size: float, guide_size_for: bool, max_size:
        float, mask_mode: bool, seed: int, steps: int, cfg: float,
        sampler_name: str, scheduler: str, denoise: float, feather: int,
        crop_factor: float, drop_size: int, refiner_ratio: float,
        batch_size: int, cycle: int, refiner_basic_pipe_opt: BASIC_PIPE,
        detailer_hook: DETAILER_HOOK, inpaint_model: bool,
        noise_mask_feather: int, bbox_fill: bool, contour_fill: bool,
        scheduler_func_opt: SCHEDULER_FUNC) ->(IMAGE, IMAGE, IMAGE,
        BASIC_PIPE, BASIC_PIPE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'mask': to_comfy_input(mask), 'basic_pipe': to_comfy_input(
            basic_pipe), 'guide_size': to_comfy_input(guide_size),
            'guide_size_for': to_comfy_input(guide_size_for), 'max_size':
            to_comfy_input(max_size), 'mask_mode': to_comfy_input(mask_mode
            ), 'seed': to_comfy_input(seed), 'steps': to_comfy_input(steps),
            'cfg': to_comfy_input(cfg), 'sampler_name': to_comfy_input(
            sampler_name), 'scheduler': to_comfy_input(scheduler),
            'denoise': to_comfy_input(denoise), 'feather': to_comfy_input(
            feather), 'crop_factor': to_comfy_input(crop_factor),
            'drop_size': to_comfy_input(drop_size), 'refiner_ratio':
            to_comfy_input(refiner_ratio), 'batch_size': to_comfy_input(
            batch_size), 'cycle': to_comfy_input(cycle),
            'refiner_basic_pipe_opt': to_comfy_input(refiner_basic_pipe_opt
            ), 'detailer_hook': to_comfy_input(detailer_hook),
            'inpaint_model': to_comfy_input(inpaint_model),
            'noise_mask_feather': to_comfy_input(noise_mask_feather),
            'bbox_fill': to_comfy_input(bbox_fill), 'contour_fill':
            to_comfy_input(contour_fill), 'scheduler_func_opt':
            to_comfy_input(scheduler_func_opt)}, 'class_type':
            'MaskDetailerPipe'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), IMAGE(node_id, 1), IMAGE(node_id, 2
            ), BASIC_PIPE(node_id, 3), BASIC_PIPE(node_id, 4)

    def ToDetailerPipe(self, model: MODEL, clip: CLIP, vae: VAE, positive:
        CONDITIONING, negative: CONDITIONING, bbox_detector: BBOX_DETECTOR,
        wildcard: str, Select_to_add_LoRA: str, Select_to_add_Wildcard: str,
        sam_model_opt: SAM_MODEL, segm_detector_opt: SEGM_DETECTOR,
        detailer_hook: DETAILER_HOOK) ->DETAILER_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'vae': to_comfy_input(vae),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'bbox_detector': to_comfy_input(
            bbox_detector), 'wildcard': to_comfy_input(wildcard),
            'Select to add LoRA': to_comfy_input(Select_to_add_LoRA),
            'Select to add Wildcard': to_comfy_input(Select_to_add_Wildcard
            ), 'sam_model_opt': to_comfy_input(sam_model_opt),
            'segm_detector_opt': to_comfy_input(segm_detector_opt),
            'detailer_hook': to_comfy_input(detailer_hook)}, 'class_type':
            'ToDetailerPipe'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_PIPE(node_id, 0)

    def ToDetailerPipeSDXL(self, model: MODEL, clip: CLIP, vae: VAE,
        positive: CONDITIONING, negative: CONDITIONING, refiner_model:
        MODEL, refiner_clip: CLIP, refiner_positive: CONDITIONING,
        refiner_negative: CONDITIONING, bbox_detector: BBOX_DETECTOR,
        wildcard: str, Select_to_add_LoRA: str, Select_to_add_Wildcard: str,
        sam_model_opt: SAM_MODEL, segm_detector_opt: SEGM_DETECTOR,
        detailer_hook: DETAILER_HOOK) ->DETAILER_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'vae': to_comfy_input(vae),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'refiner_model': to_comfy_input(
            refiner_model), 'refiner_clip': to_comfy_input(refiner_clip),
            'refiner_positive': to_comfy_input(refiner_positive),
            'refiner_negative': to_comfy_input(refiner_negative),
            'bbox_detector': to_comfy_input(bbox_detector), 'wildcard':
            to_comfy_input(wildcard), 'Select to add LoRA': to_comfy_input(
            Select_to_add_LoRA), 'Select to add Wildcard': to_comfy_input(
            Select_to_add_Wildcard), 'sam_model_opt': to_comfy_input(
            sam_model_opt), 'segm_detector_opt': to_comfy_input(
            segm_detector_opt), 'detailer_hook': to_comfy_input(
            detailer_hook)}, 'class_type': 'ToDetailerPipeSDXL'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_PIPE(node_id, 0)

    def FromDetailerPipe(self, detailer_pipe: DETAILER_PIPE) ->(MODEL, CLIP,
        VAE, CONDITIONING, CONDITIONING, BBOX_DETECTOR, SAM_MODEL,
        SEGM_DETECTOR, DETAILER_HOOK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'detailer_pipe': to_comfy_input(
            detailer_pipe)}, 'class_type': 'FromDetailerPipe'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP(node_id, 1), VAE(node_id, 2
            ), CONDITIONING(node_id, 3), CONDITIONING(node_id, 4
            ), BBOX_DETECTOR(node_id, 5), SAM_MODEL(node_id, 6), SEGM_DETECTOR(
            node_id, 7), DETAILER_HOOK(node_id, 8)

    def FromDetailerPipe_v2(self, detailer_pipe: DETAILER_PIPE) ->(
        DETAILER_PIPE, MODEL, CLIP, VAE, CONDITIONING, CONDITIONING,
        BBOX_DETECTOR, SAM_MODEL, SEGM_DETECTOR, DETAILER_HOOK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'detailer_pipe': to_comfy_input(
            detailer_pipe)}, 'class_type': 'FromDetailerPipe_v2'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_PIPE(node_id, 0), MODEL(node_id, 1), CLIP(node_id, 2
            ), VAE(node_id, 3), CONDITIONING(node_id, 4), CONDITIONING(node_id,
            5), BBOX_DETECTOR(node_id, 6), SAM_MODEL(node_id, 7
            ), SEGM_DETECTOR(node_id, 8), DETAILER_HOOK(node_id, 9)

    def FromDetailerPipeSDXL(self, detailer_pipe: DETAILER_PIPE) ->(
        DETAILER_PIPE, MODEL, CLIP, VAE, CONDITIONING, CONDITIONING,
        BBOX_DETECTOR, SAM_MODEL, SEGM_DETECTOR, DETAILER_HOOK, MODEL, CLIP,
        CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'detailer_pipe': to_comfy_input(
            detailer_pipe)}, 'class_type': 'FromDetailerPipeSDXL'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_PIPE(node_id, 0), MODEL(node_id, 1), CLIP(node_id, 2
            ), VAE(node_id, 3), CONDITIONING(node_id, 4), CONDITIONING(node_id,
            5), BBOX_DETECTOR(node_id, 6), SAM_MODEL(node_id, 7
            ), SEGM_DETECTOR(node_id, 8), DETAILER_HOOK(node_id, 9), MODEL(
            node_id, 10), CLIP(node_id, 11), CONDITIONING(node_id, 12
            ), CONDITIONING(node_id, 13)

    def AnyPipeToBasic(self, any_pipe: AnyNodeOutput) ->BASIC_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'any_pipe': to_comfy_input(any_pipe)},
            'class_type': 'AnyPipeToBasic'}
        self._add_node(node_id, comfy_json_node)
        return BASIC_PIPE(node_id, 0)

    def ToBasicPipe(self, model: MODEL, clip: CLIP, vae: VAE, positive:
        CONDITIONING, negative: CONDITIONING) ->BASIC_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'vae': to_comfy_input(vae),
            'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative)}, 'class_type': 'ToBasicPipe'}
        self._add_node(node_id, comfy_json_node)
        return BASIC_PIPE(node_id, 0)

    def FromBasicPipe(self, basic_pipe: BASIC_PIPE) ->(MODEL, CLIP, VAE,
        CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'basic_pipe': to_comfy_input(
            basic_pipe)}, 'class_type': 'FromBasicPipe'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP(node_id, 1), VAE(node_id, 2
            ), CONDITIONING(node_id, 3), CONDITIONING(node_id, 4)

    def FromBasicPipe_v2(self, basic_pipe: BASIC_PIPE) ->(BASIC_PIPE, MODEL,
        CLIP, VAE, CONDITIONING, CONDITIONING):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'basic_pipe': to_comfy_input(
            basic_pipe)}, 'class_type': 'FromBasicPipe_v2'}
        self._add_node(node_id, comfy_json_node)
        return BASIC_PIPE(node_id, 0), MODEL(node_id, 1), CLIP(node_id, 2
            ), VAE(node_id, 3), CONDITIONING(node_id, 4), CONDITIONING(node_id,
            5)

    def BasicPipeToDetailerPipe(self, basic_pipe: BASIC_PIPE, bbox_detector:
        BBOX_DETECTOR, wildcard: str, Select_to_add_LoRA: str,
        Select_to_add_Wildcard: str, sam_model_opt: SAM_MODEL,
        segm_detector_opt: SEGM_DETECTOR, detailer_hook: DETAILER_HOOK
        ) ->DETAILER_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'basic_pipe': to_comfy_input(
            basic_pipe), 'bbox_detector': to_comfy_input(bbox_detector),
            'wildcard': to_comfy_input(wildcard), 'Select to add LoRA':
            to_comfy_input(Select_to_add_LoRA), 'Select to add Wildcard':
            to_comfy_input(Select_to_add_Wildcard), 'sam_model_opt':
            to_comfy_input(sam_model_opt), 'segm_detector_opt':
            to_comfy_input(segm_detector_opt), 'detailer_hook':
            to_comfy_input(detailer_hook)}, 'class_type':
            'BasicPipeToDetailerPipe'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_PIPE(node_id, 0)

    def BasicPipeToDetailerPipeSDXL(self, base_basic_pipe: BASIC_PIPE,
        refiner_basic_pipe: BASIC_PIPE, bbox_detector: BBOX_DETECTOR,
        wildcard: str, Select_to_add_LoRA: str, Select_to_add_Wildcard: str,
        sam_model_opt: SAM_MODEL, segm_detector_opt: SEGM_DETECTOR,
        detailer_hook: DETAILER_HOOK) ->DETAILER_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'base_basic_pipe': to_comfy_input(
            base_basic_pipe), 'refiner_basic_pipe': to_comfy_input(
            refiner_basic_pipe), 'bbox_detector': to_comfy_input(
            bbox_detector), 'wildcard': to_comfy_input(wildcard),
            'Select to add LoRA': to_comfy_input(Select_to_add_LoRA),
            'Select to add Wildcard': to_comfy_input(Select_to_add_Wildcard
            ), 'sam_model_opt': to_comfy_input(sam_model_opt),
            'segm_detector_opt': to_comfy_input(segm_detector_opt),
            'detailer_hook': to_comfy_input(detailer_hook)}, 'class_type':
            'BasicPipeToDetailerPipeSDXL'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_PIPE(node_id, 0)

    def DetailerPipeToBasicPipe(self, detailer_pipe: DETAILER_PIPE) ->(
        BASIC_PIPE, BASIC_PIPE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'detailer_pipe': to_comfy_input(
            detailer_pipe)}, 'class_type': 'DetailerPipeToBasicPipe'}
        self._add_node(node_id, comfy_json_node)
        return BASIC_PIPE(node_id, 0), BASIC_PIPE(node_id, 1)

    def EditBasicPipe(self, basic_pipe: BASIC_PIPE, model: MODEL, clip:
        CLIP, vae: VAE, positive: CONDITIONING, negative: CONDITIONING
        ) ->BASIC_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'basic_pipe': to_comfy_input(
            basic_pipe), 'model': to_comfy_input(model), 'clip':
            to_comfy_input(clip), 'vae': to_comfy_input(vae), 'positive':
            to_comfy_input(positive), 'negative': to_comfy_input(negative)},
            'class_type': 'EditBasicPipe'}
        self._add_node(node_id, comfy_json_node)
        return BASIC_PIPE(node_id, 0)

    def EditDetailerPipe(self, detailer_pipe: DETAILER_PIPE, wildcard: str,
        Select_to_add_LoRA: str, Select_to_add_Wildcard: str, model: MODEL,
        clip: CLIP, vae: VAE, positive: CONDITIONING, negative:
        CONDITIONING, bbox_detector: BBOX_DETECTOR, sam_model: SAM_MODEL,
        segm_detector: SEGM_DETECTOR, detailer_hook: DETAILER_HOOK
        ) ->DETAILER_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'detailer_pipe': to_comfy_input(
            detailer_pipe), 'wildcard': to_comfy_input(wildcard),
            'Select to add LoRA': to_comfy_input(Select_to_add_LoRA),
            'Select to add Wildcard': to_comfy_input(Select_to_add_Wildcard
            ), 'model': to_comfy_input(model), 'clip': to_comfy_input(clip),
            'vae': to_comfy_input(vae), 'positive': to_comfy_input(positive
            ), 'negative': to_comfy_input(negative), 'bbox_detector':
            to_comfy_input(bbox_detector), 'sam_model': to_comfy_input(
            sam_model), 'segm_detector': to_comfy_input(segm_detector),
            'detailer_hook': to_comfy_input(detailer_hook)}, 'class_type':
            'EditDetailerPipe'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_PIPE(node_id, 0)

    def EditDetailerPipeSDXL(self, detailer_pipe: DETAILER_PIPE, wildcard:
        str, Select_to_add_LoRA: str, Select_to_add_Wildcard: str, model:
        MODEL, clip: CLIP, vae: VAE, positive: CONDITIONING, negative:
        CONDITIONING, refiner_model: MODEL, refiner_clip: CLIP,
        refiner_positive: CONDITIONING, refiner_negative: CONDITIONING,
        bbox_detector: BBOX_DETECTOR, sam_model: SAM_MODEL, segm_detector:
        SEGM_DETECTOR, detailer_hook: DETAILER_HOOK) ->DETAILER_PIPE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'detailer_pipe': to_comfy_input(
            detailer_pipe), 'wildcard': to_comfy_input(wildcard),
            'Select to add LoRA': to_comfy_input(Select_to_add_LoRA),
            'Select to add Wildcard': to_comfy_input(Select_to_add_Wildcard
            ), 'model': to_comfy_input(model), 'clip': to_comfy_input(clip),
            'vae': to_comfy_input(vae), 'positive': to_comfy_input(positive
            ), 'negative': to_comfy_input(negative), 'refiner_model':
            to_comfy_input(refiner_model), 'refiner_clip': to_comfy_input(
            refiner_clip), 'refiner_positive': to_comfy_input(
            refiner_positive), 'refiner_negative': to_comfy_input(
            refiner_negative), 'bbox_detector': to_comfy_input(
            bbox_detector), 'sam_model': to_comfy_input(sam_model),
            'segm_detector': to_comfy_input(segm_detector), 'detailer_hook':
            to_comfy_input(detailer_hook)}, 'class_type':
            'EditDetailerPipeSDXL'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_PIPE(node_id, 0)

    def LatentPixelScale(self, samples: LATENT, scale_method: str,
        scale_factor: float, vae: VAE, use_tiled_vae: bool,
        upscale_model_opt: UPSCALE_MODEL) ->(LATENT, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'scale_method': to_comfy_input(scale_method), 'scale_factor':
            to_comfy_input(scale_factor), 'vae': to_comfy_input(vae),
            'use_tiled_vae': to_comfy_input(use_tiled_vae),
            'upscale_model_opt': to_comfy_input(upscale_model_opt)},
            'class_type': 'LatentPixelScale'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0), IMAGE(node_id, 1)

    def PixelKSampleUpscalerProvider(self, scale_method: str, model: MODEL,
        vae: VAE, seed: int, steps: int, cfg: float, sampler_name: str,
        scheduler: str, positive: CONDITIONING, negative: CONDITIONING,
        denoise: float, use_tiled_vae: bool, tile_size: int,
        upscale_model_opt: UPSCALE_MODEL, pk_hook_opt: PK_HOOK,
        scheduler_func_opt: SCHEDULER_FUNC) ->UPSCALER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'scale_method': to_comfy_input(
            scale_method), 'model': to_comfy_input(model), 'vae':
            to_comfy_input(vae), 'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'denoise': to_comfy_input
            (denoise), 'use_tiled_vae': to_comfy_input(use_tiled_vae),
            'tile_size': to_comfy_input(tile_size), 'upscale_model_opt':
            to_comfy_input(upscale_model_opt), 'pk_hook_opt':
            to_comfy_input(pk_hook_opt), 'scheduler_func_opt':
            to_comfy_input(scheduler_func_opt)}, 'class_type':
            'PixelKSampleUpscalerProvider'}
        self._add_node(node_id, comfy_json_node)
        return UPSCALER(node_id, 0)

    def PixelKSampleUpscalerProviderPipe(self, scale_method: str, seed: int,
        steps: int, cfg: float, sampler_name: str, scheduler: str, denoise:
        float, use_tiled_vae: bool, basic_pipe: BASIC_PIPE, tile_size: int,
        upscale_model_opt: UPSCALE_MODEL, pk_hook_opt: PK_HOOK,
        scheduler_func_opt: SCHEDULER_FUNC, tile_cnet_opt: CONTROL_NET,
        tile_cnet_strength: float) ->UPSCALER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'scale_method': to_comfy_input(
            scale_method), 'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'use_tiled_vae': to_comfy_input(use_tiled_vae), 'basic_pipe':
            to_comfy_input(basic_pipe), 'tile_size': to_comfy_input(
            tile_size), 'upscale_model_opt': to_comfy_input(
            upscale_model_opt), 'pk_hook_opt': to_comfy_input(pk_hook_opt),
            'scheduler_func_opt': to_comfy_input(scheduler_func_opt),
            'tile_cnet_opt': to_comfy_input(tile_cnet_opt),
            'tile_cnet_strength': to_comfy_input(tile_cnet_strength)},
            'class_type': 'PixelKSampleUpscalerProviderPipe'}
        self._add_node(node_id, comfy_json_node)
        return UPSCALER(node_id, 0)

    def IterativeLatentUpscale(self, samples: LATENT, upscale_factor: float,
        steps: int, temp_prefix: str, upscaler: UPSCALER, step_mode: str) ->(
        LATENT, VAE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'upscale_factor': to_comfy_input(upscale_factor), 'steps':
            to_comfy_input(steps), 'temp_prefix': to_comfy_input(
            temp_prefix), 'upscaler': to_comfy_input(upscaler), 'step_mode':
            to_comfy_input(step_mode)}, 'class_type': 'IterativeLatentUpscale'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0), VAE(node_id, 1)

    def IterativeImageUpscale(self, pixels: IMAGE, upscale_factor: float,
        steps: int, temp_prefix: str, upscaler: UPSCALER, vae: VAE,
        step_mode: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'pixels': to_comfy_input(pixels),
            'upscale_factor': to_comfy_input(upscale_factor), 'steps':
            to_comfy_input(steps), 'temp_prefix': to_comfy_input(
            temp_prefix), 'upscaler': to_comfy_input(upscaler), 'vae':
            to_comfy_input(vae), 'step_mode': to_comfy_input(step_mode)},
            'class_type': 'IterativeImageUpscale'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def PixelTiledKSampleUpscalerProvider(self, scale_method: str, model:
        MODEL, vae: VAE, seed: int, steps: int, cfg: float, sampler_name:
        str, scheduler: str, positive: CONDITIONING, negative: CONDITIONING,
        denoise: float, tile_width: int, tile_height: int, tiling_strategy:
        str, upscale_model_opt: UPSCALE_MODEL, pk_hook_opt: PK_HOOK,
        tile_cnet_opt: CONTROL_NET, tile_cnet_strength: float, overlap: int
        ) ->UPSCALER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'scale_method': to_comfy_input(
            scale_method), 'model': to_comfy_input(model), 'vae':
            to_comfy_input(vae), 'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'denoise': to_comfy_input
            (denoise), 'tile_width': to_comfy_input(tile_width),
            'tile_height': to_comfy_input(tile_height), 'tiling_strategy':
            to_comfy_input(tiling_strategy), 'upscale_model_opt':
            to_comfy_input(upscale_model_opt), 'pk_hook_opt':
            to_comfy_input(pk_hook_opt), 'tile_cnet_opt': to_comfy_input(
            tile_cnet_opt), 'tile_cnet_strength': to_comfy_input(
            tile_cnet_strength), 'overlap': to_comfy_input(overlap)},
            'class_type': 'PixelTiledKSampleUpscalerProvider'}
        self._add_node(node_id, comfy_json_node)
        return UPSCALER(node_id, 0)

    def PixelTiledKSampleUpscalerProviderPipe(self, scale_method: str, seed:
        int, steps: int, cfg: float, sampler_name: str, scheduler: str,
        denoise: float, tile_width: int, tile_height: int, tiling_strategy:
        str, basic_pipe: BASIC_PIPE, upscale_model_opt: UPSCALE_MODEL,
        pk_hook_opt: PK_HOOK, tile_cnet_opt: CONTROL_NET,
        tile_cnet_strength: float) ->UPSCALER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'scale_method': to_comfy_input(
            scale_method), 'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'tile_width': to_comfy_input(tile_width), 'tile_height':
            to_comfy_input(tile_height), 'tiling_strategy': to_comfy_input(
            tiling_strategy), 'basic_pipe': to_comfy_input(basic_pipe),
            'upscale_model_opt': to_comfy_input(upscale_model_opt),
            'pk_hook_opt': to_comfy_input(pk_hook_opt), 'tile_cnet_opt':
            to_comfy_input(tile_cnet_opt), 'tile_cnet_strength':
            to_comfy_input(tile_cnet_strength)}, 'class_type':
            'PixelTiledKSampleUpscalerProviderPipe'}
        self._add_node(node_id, comfy_json_node)
        return UPSCALER(node_id, 0)

    def TwoSamplersForMaskUpscalerProvider(self, scale_method: str,
        full_sample_schedule: str, use_tiled_vae: bool, base_sampler:
        KSAMPLER, mask_sampler: KSAMPLER, mask: MASK, vae: VAE, tile_size:
        int, full_sampler_opt: KSAMPLER, upscale_model_opt: UPSCALE_MODEL,
        pk_hook_base_opt: PK_HOOK, pk_hook_mask_opt: PK_HOOK,
        pk_hook_full_opt: PK_HOOK) ->UPSCALER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'scale_method': to_comfy_input(
            scale_method), 'full_sample_schedule': to_comfy_input(
            full_sample_schedule), 'use_tiled_vae': to_comfy_input(
            use_tiled_vae), 'base_sampler': to_comfy_input(base_sampler),
            'mask_sampler': to_comfy_input(mask_sampler), 'mask':
            to_comfy_input(mask), 'vae': to_comfy_input(vae), 'tile_size':
            to_comfy_input(tile_size), 'full_sampler_opt': to_comfy_input(
            full_sampler_opt), 'upscale_model_opt': to_comfy_input(
            upscale_model_opt), 'pk_hook_base_opt': to_comfy_input(
            pk_hook_base_opt), 'pk_hook_mask_opt': to_comfy_input(
            pk_hook_mask_opt), 'pk_hook_full_opt': to_comfy_input(
            pk_hook_full_opt)}, 'class_type':
            'TwoSamplersForMaskUpscalerProvider'}
        self._add_node(node_id, comfy_json_node)
        return UPSCALER(node_id, 0)

    def TwoSamplersForMaskUpscalerProviderPipe(self, scale_method: str,
        full_sample_schedule: str, use_tiled_vae: bool, base_sampler:
        KSAMPLER, mask_sampler: KSAMPLER, mask: MASK, basic_pipe:
        BASIC_PIPE, tile_size: int, full_sampler_opt: KSAMPLER,
        upscale_model_opt: UPSCALE_MODEL, pk_hook_base_opt: PK_HOOK,
        pk_hook_mask_opt: PK_HOOK, pk_hook_full_opt: PK_HOOK) ->UPSCALER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'scale_method': to_comfy_input(
            scale_method), 'full_sample_schedule': to_comfy_input(
            full_sample_schedule), 'use_tiled_vae': to_comfy_input(
            use_tiled_vae), 'base_sampler': to_comfy_input(base_sampler),
            'mask_sampler': to_comfy_input(mask_sampler), 'mask':
            to_comfy_input(mask), 'basic_pipe': to_comfy_input(basic_pipe),
            'tile_size': to_comfy_input(tile_size), 'full_sampler_opt':
            to_comfy_input(full_sampler_opt), 'upscale_model_opt':
            to_comfy_input(upscale_model_opt), 'pk_hook_base_opt':
            to_comfy_input(pk_hook_base_opt), 'pk_hook_mask_opt':
            to_comfy_input(pk_hook_mask_opt), 'pk_hook_full_opt':
            to_comfy_input(pk_hook_full_opt)}, 'class_type':
            'TwoSamplersForMaskUpscalerProviderPipe'}
        self._add_node(node_id, comfy_json_node)
        return UPSCALER(node_id, 0)

    def PixelKSampleHookCombine(self, hook1: PK_HOOK, hook2: PK_HOOK
        ) ->PK_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'hook1': to_comfy_input(hook1),
            'hook2': to_comfy_input(hook2)}, 'class_type':
            'PixelKSampleHookCombine'}
        self._add_node(node_id, comfy_json_node)
        return PK_HOOK(node_id, 0)

    def DenoiseScheduleHookProvider(self, schedule_for_iteration: str,
        target_denoise: float) ->PK_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'schedule_for_iteration':
            to_comfy_input(schedule_for_iteration), 'target_denoise':
            to_comfy_input(target_denoise)}, 'class_type':
            'DenoiseScheduleHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return PK_HOOK(node_id, 0)

    def StepsScheduleHookProvider(self, schedule_for_iteration: str,
        target_steps: int) ->PK_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'schedule_for_iteration':
            to_comfy_input(schedule_for_iteration), 'target_steps':
            to_comfy_input(target_steps)}, 'class_type':
            'StepsScheduleHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return PK_HOOK(node_id, 0)

    def CfgScheduleHookProvider(self, schedule_for_iteration: str,
        target_cfg: float) ->PK_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'schedule_for_iteration':
            to_comfy_input(schedule_for_iteration), 'target_cfg':
            to_comfy_input(target_cfg)}, 'class_type':
            'CfgScheduleHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return PK_HOOK(node_id, 0)

    def NoiseInjectionHookProvider(self, schedule_for_iteration: str,
        source: str, seed: int, start_strength: float, end_strength: float
        ) ->PK_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'schedule_for_iteration':
            to_comfy_input(schedule_for_iteration), 'source':
            to_comfy_input(source), 'seed': to_comfy_input(seed),
            'start_strength': to_comfy_input(start_strength),
            'end_strength': to_comfy_input(end_strength)}, 'class_type':
            'NoiseInjectionHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return PK_HOOK(node_id, 0)

    def UnsamplerHookProvider(self, model: MODEL, steps: int,
        start_end_at_step: int, end_end_at_step: int, cfg: float,
        sampler_name: str, scheduler: str, normalize: str, positive:
        CONDITIONING, negative: CONDITIONING, schedule_for_iteration: str
        ) ->PK_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'steps': to_comfy_input(steps), 'start_end_at_step':
            to_comfy_input(start_end_at_step), 'end_end_at_step':
            to_comfy_input(end_end_at_step), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'normalize': to_comfy_input(
            normalize), 'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'schedule_for_iteration':
            to_comfy_input(schedule_for_iteration)}, 'class_type':
            'UnsamplerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return PK_HOOK(node_id, 0)

    def CoreMLDetailerHookProvider(self, mode: str) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mode': to_comfy_input(mode)},
            'class_type': 'CoreMLDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def PreviewDetailerHookProvider(self, quality: int) ->(DETAILER_HOOK,
        UPSCALER_HOOK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'quality': to_comfy_input(quality)},
            'class_type': 'PreviewDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0), UPSCALER_HOOK(node_id, 1)

    def BlackPatchRetryHookProvider(self, mean_thresh: int, var_thresh: int
        ) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mean_thresh': to_comfy_input(
            mean_thresh), 'var_thresh': to_comfy_input(var_thresh)},
            'class_type': 'BlackPatchRetryHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def CustomSamplerDetailerHookProvider(self, sampler: SAMPLER
        ) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'sampler': to_comfy_input(sampler)},
            'class_type': 'CustomSamplerDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def LamaRemoverDetailerHookProvider(self, mask_threshold: int,
        gaussblur_radius: int, skip_sampling: bool) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask_threshold': to_comfy_input(
            mask_threshold), 'gaussblur_radius': to_comfy_input(
            gaussblur_radius), 'skip_sampling': to_comfy_input(
            skip_sampling)}, 'class_type': 'LamaRemoverDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def DetailerHookCombine(self, hook1: DETAILER_HOOK, hook2: DETAILER_HOOK
        ) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'hook1': to_comfy_input(hook1),
            'hook2': to_comfy_input(hook2)}, 'class_type':
            'DetailerHookCombine'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def NoiseInjectionDetailerHookProvider(self, schedule_for_cycle: str,
        source: str, seed: int, start_strength: float, end_strength: float
        ) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'schedule_for_cycle': to_comfy_input(
            schedule_for_cycle), 'source': to_comfy_input(source), 'seed':
            to_comfy_input(seed), 'start_strength': to_comfy_input(
            start_strength), 'end_strength': to_comfy_input(end_strength)},
            'class_type': 'NoiseInjectionDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def UnsamplerDetailerHookProvider(self, model: MODEL, steps: int,
        start_end_at_step: int, end_end_at_step: int, cfg: float,
        sampler_name: str, scheduler: str, normalize: str, positive:
        CONDITIONING, negative: CONDITIONING, schedule_for_cycle: str
        ) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'steps': to_comfy_input(steps), 'start_end_at_step':
            to_comfy_input(start_end_at_step), 'end_end_at_step':
            to_comfy_input(end_end_at_step), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'normalize': to_comfy_input(
            normalize), 'positive': to_comfy_input(positive), 'negative':
            to_comfy_input(negative), 'schedule_for_cycle': to_comfy_input(
            schedule_for_cycle)}, 'class_type': 'UnsamplerDetailerHookProvider'
            }
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def DenoiseSchedulerDetailerHookProvider(self, schedule_for_cycle: str,
        target_denoise: float) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'schedule_for_cycle': to_comfy_input(
            schedule_for_cycle), 'target_denoise': to_comfy_input(
            target_denoise)}, 'class_type':
            'DenoiseSchedulerDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def SEGSOrderedFilterDetailerHookProvider(self, target: str, order:
        bool, take_start: int, take_count: int) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'target': to_comfy_input(target),
            'order': to_comfy_input(order), 'take_start': to_comfy_input(
            take_start), 'take_count': to_comfy_input(take_count)},
            'class_type': 'SEGSOrderedFilterDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def SEGSRangeFilterDetailerHookProvider(self, target: str, mode: bool,
        min_value: int, max_value: int) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'target': to_comfy_input(target),
            'mode': to_comfy_input(mode), 'min_value': to_comfy_input(
            min_value), 'max_value': to_comfy_input(max_value)},
            'class_type': 'SEGSRangeFilterDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def SEGSLabelFilterDetailerHookProvider(self, segs: SEGS, preset: str,
        labels: str) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'preset': to_comfy_input(preset), 'labels': to_comfy_input(
            labels)}, 'class_type': 'SEGSLabelFilterDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def VariationNoiseDetailerHookProvider(self, seed: int, strength: float
        ) ->DETAILER_HOOK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seed': to_comfy_input(seed),
            'strength': to_comfy_input(strength)}, 'class_type':
            'VariationNoiseDetailerHookProvider'}
        self._add_node(node_id, comfy_json_node)
        return DETAILER_HOOK(node_id, 0)

    def BitwiseAndMask(self, mask1: MASK, mask2: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask1': to_comfy_input(mask1),
            'mask2': to_comfy_input(mask2)}, 'class_type': 'BitwiseAndMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def SubtractMask(self, mask1: MASK, mask2: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask1': to_comfy_input(mask1),
            'mask2': to_comfy_input(mask2)}, 'class_type': 'SubtractMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def AddMask(self, mask1: MASK, mask2: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask1': to_comfy_input(mask1),
            'mask2': to_comfy_input(mask2)}, 'class_type': 'AddMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def MaskRectArea(self) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {}, 'class_type': 'MaskRectArea'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def MaskRectAreaAdvanced(self) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {}, 'class_type': 'MaskRectAreaAdvanced'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImpactSegsAndMask(self, segs: SEGS, mask: MASK) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs), 'mask':
            to_comfy_input(mask)}, 'class_type': 'ImpactSegsAndMask'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSegsAndMaskForEach(self, segs: SEGS, masks: MASK) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs), 'masks':
            to_comfy_input(masks)}, 'class_type': 'ImpactSegsAndMaskForEach'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def EmptySegs(self) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {}, 'class_type': 'EmptySegs'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactFlattenMask(self, masks: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'masks': to_comfy_input(masks)},
            'class_type': 'ImpactFlattenMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def MediaPipeFaceMeshToSEGS(self, image: IMAGE, crop_factor: float,
        bbox_fill: bool, crop_min_size: int, drop_size: int, dilation: int,
        face: bool, mouth: bool, left_eyebrow: bool, left_eye: bool,
        left_pupil: bool, right_eyebrow: bool, right_eye: bool, right_pupil:
        bool) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'crop_factor': to_comfy_input(crop_factor), 'bbox_fill':
            to_comfy_input(bbox_fill), 'crop_min_size': to_comfy_input(
            crop_min_size), 'drop_size': to_comfy_input(drop_size),
            'dilation': to_comfy_input(dilation), 'face': to_comfy_input(
            face), 'mouth': to_comfy_input(mouth), 'left_eyebrow':
            to_comfy_input(left_eyebrow), 'left_eye': to_comfy_input(
            left_eye), 'left_pupil': to_comfy_input(left_pupil),
            'right_eyebrow': to_comfy_input(right_eyebrow), 'right_eye':
            to_comfy_input(right_eye), 'right_pupil': to_comfy_input(
            right_pupil)}, 'class_type': 'MediaPipeFaceMeshToSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def MaskToSEGS(self, mask: MASK, combined: bool, crop_factor: float,
        bbox_fill: bool, drop_size: int, contour_fill: bool) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask),
            'combined': to_comfy_input(combined), 'crop_factor':
            to_comfy_input(crop_factor), 'bbox_fill': to_comfy_input(
            bbox_fill), 'drop_size': to_comfy_input(drop_size),
            'contour_fill': to_comfy_input(contour_fill)}, 'class_type':
            'MaskToSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def MaskToSEGS_for_AnimateDiff(self, mask: MASK, combined: bool,
        crop_factor: float, bbox_fill: bool, drop_size: int, contour_fill: bool
        ) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask),
            'combined': to_comfy_input(combined), 'crop_factor':
            to_comfy_input(crop_factor), 'bbox_fill': to_comfy_input(
            bbox_fill), 'drop_size': to_comfy_input(drop_size),
            'contour_fill': to_comfy_input(contour_fill)}, 'class_type':
            'MaskToSEGS_for_AnimateDiff'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ToBinaryMask(self, mask: MASK, threshold: int) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask),
            'threshold': to_comfy_input(threshold)}, 'class_type':
            'ToBinaryMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def MasksToMaskList(self, masks: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'masks': to_comfy_input(masks)},
            'class_type': 'MasksToMaskList'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def MaskListToMaskBatch(self, mask: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask)},
            'class_type': 'MaskListToMaskBatch'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImageListToImageBatch(self, images: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images)},
            'class_type': 'ImageListToImageBatch'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SetDefaultImageForSEGS(self, segs: SEGS, image: IMAGE, override: bool
        ) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs), 'image':
            to_comfy_input(image), 'override': to_comfy_input(override)},
            'class_type': 'SetDefaultImageForSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def RemoveImageFromSEGS(self, segs: SEGS) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'RemoveImageFromSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def BboxDetectorSEGS(self, bbox_detector: BBOX_DETECTOR, image: IMAGE,
        threshold: float, dilation: int, crop_factor: float, drop_size: int,
        labels: str, detailer_hook: DETAILER_HOOK) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'bbox_detector': to_comfy_input(
            bbox_detector), 'image': to_comfy_input(image), 'threshold':
            to_comfy_input(threshold), 'dilation': to_comfy_input(dilation),
            'crop_factor': to_comfy_input(crop_factor), 'drop_size':
            to_comfy_input(drop_size), 'labels': to_comfy_input(labels),
            'detailer_hook': to_comfy_input(detailer_hook)}, 'class_type':
            'BboxDetectorSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def SegmDetectorSEGS(self, segm_detector: SEGM_DETECTOR, image: IMAGE,
        threshold: float, dilation: int, crop_factor: float, drop_size: int,
        labels: str, detailer_hook: DETAILER_HOOK) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segm_detector': to_comfy_input(
            segm_detector), 'image': to_comfy_input(image), 'threshold':
            to_comfy_input(threshold), 'dilation': to_comfy_input(dilation),
            'crop_factor': to_comfy_input(crop_factor), 'drop_size':
            to_comfy_input(drop_size), 'labels': to_comfy_input(labels),
            'detailer_hook': to_comfy_input(detailer_hook)}, 'class_type':
            'SegmDetectorSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ONNXDetectorSEGS(self, bbox_detector: BBOX_DETECTOR, image: IMAGE,
        threshold: float, dilation: int, crop_factor: float, drop_size: int,
        labels: str, detailer_hook: DETAILER_HOOK) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'bbox_detector': to_comfy_input(
            bbox_detector), 'image': to_comfy_input(image), 'threshold':
            to_comfy_input(threshold), 'dilation': to_comfy_input(dilation),
            'crop_factor': to_comfy_input(crop_factor), 'drop_size':
            to_comfy_input(drop_size), 'labels': to_comfy_input(labels),
            'detailer_hook': to_comfy_input(detailer_hook)}, 'class_type':
            'ONNXDetectorSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSimpleDetectorSEGS_for_AD(self, bbox_detector: BBOX_DETECTOR,
        image_frames: IMAGE, bbox_threshold: float, bbox_dilation: int,
        crop_factor: float, drop_size: int, sub_threshold: float,
        sub_dilation: int, sub_bbox_expansion: int, sam_mask_hint_threshold:
        float, masking_mode: str, segs_pivot: str, sam_model_opt: SAM_MODEL,
        segm_detector_opt: SEGM_DETECTOR) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'bbox_detector': to_comfy_input(
            bbox_detector), 'image_frames': to_comfy_input(image_frames),
            'bbox_threshold': to_comfy_input(bbox_threshold),
            'bbox_dilation': to_comfy_input(bbox_dilation), 'crop_factor':
            to_comfy_input(crop_factor), 'drop_size': to_comfy_input(
            drop_size), 'sub_threshold': to_comfy_input(sub_threshold),
            'sub_dilation': to_comfy_input(sub_dilation),
            'sub_bbox_expansion': to_comfy_input(sub_bbox_expansion),
            'sam_mask_hint_threshold': to_comfy_input(
            sam_mask_hint_threshold), 'masking_mode': to_comfy_input(
            masking_mode), 'segs_pivot': to_comfy_input(segs_pivot),
            'sam_model_opt': to_comfy_input(sam_model_opt),
            'segm_detector_opt': to_comfy_input(segm_detector_opt)},
            'class_type': 'ImpactSimpleDetectorSEGS_for_AD'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSAM2VideoDetectorSEGS(self, image_frames: IMAGE,
        bbox_detector: BBOX_DETECTOR, sam2_model: SAM_MODEL, bbox_threshold:
        float, sam2_threshold: float, crop_factor: float, drop_size: int
        ) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image_frames': to_comfy_input(
            image_frames), 'bbox_detector': to_comfy_input(bbox_detector),
            'sam2_model': to_comfy_input(sam2_model), 'bbox_threshold':
            to_comfy_input(bbox_threshold), 'sam2_threshold':
            to_comfy_input(sam2_threshold), 'crop_factor': to_comfy_input(
            crop_factor), 'drop_size': to_comfy_input(drop_size)},
            'class_type': 'ImpactSAM2VideoDetectorSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSimpleDetectorSEGS(self, bbox_detector: BBOX_DETECTOR, image:
        IMAGE, bbox_threshold: float, bbox_dilation: int, crop_factor:
        float, drop_size: int, sub_threshold: float, sub_dilation: int,
        sub_bbox_expansion: int, sam_mask_hint_threshold: float,
        post_dilation: int, sam_model_opt: SAM_MODEL, segm_detector_opt:
        SEGM_DETECTOR) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'bbox_detector': to_comfy_input(
            bbox_detector), 'image': to_comfy_input(image),
            'bbox_threshold': to_comfy_input(bbox_threshold),
            'bbox_dilation': to_comfy_input(bbox_dilation), 'crop_factor':
            to_comfy_input(crop_factor), 'drop_size': to_comfy_input(
            drop_size), 'sub_threshold': to_comfy_input(sub_threshold),
            'sub_dilation': to_comfy_input(sub_dilation),
            'sub_bbox_expansion': to_comfy_input(sub_bbox_expansion),
            'sam_mask_hint_threshold': to_comfy_input(
            sam_mask_hint_threshold), 'post_dilation': to_comfy_input(
            post_dilation), 'sam_model_opt': to_comfy_input(sam_model_opt),
            'segm_detector_opt': to_comfy_input(segm_detector_opt)},
            'class_type': 'ImpactSimpleDetectorSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSimpleDetectorSEGSPipe(self, detailer_pipe: DETAILER_PIPE,
        image: IMAGE, bbox_threshold: float, bbox_dilation: int,
        crop_factor: float, drop_size: int, sub_threshold: float,
        sub_dilation: int, sub_bbox_expansion: int, sam_mask_hint_threshold:
        float, post_dilation: int) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'detailer_pipe': to_comfy_input(
            detailer_pipe), 'image': to_comfy_input(image),
            'bbox_threshold': to_comfy_input(bbox_threshold),
            'bbox_dilation': to_comfy_input(bbox_dilation), 'crop_factor':
            to_comfy_input(crop_factor), 'drop_size': to_comfy_input(
            drop_size), 'sub_threshold': to_comfy_input(sub_threshold),
            'sub_dilation': to_comfy_input(sub_dilation),
            'sub_bbox_expansion': to_comfy_input(sub_bbox_expansion),
            'sam_mask_hint_threshold': to_comfy_input(
            sam_mask_hint_threshold), 'post_dilation': to_comfy_input(
            post_dilation)}, 'class_type': 'ImpactSimpleDetectorSEGSPipe'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactControlNetApplySEGS(self, segs: SEGS, control_net:
        CONTROL_NET, strength: float, segs_preprocessor: SEGS_PREPROCESSOR,
        control_image: IMAGE) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'control_net': to_comfy_input(control_net), 'strength':
            to_comfy_input(strength), 'segs_preprocessor': to_comfy_input(
            segs_preprocessor), 'control_image': to_comfy_input(
            control_image)}, 'class_type': 'ImpactControlNetApplySEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactControlNetApplyAdvancedSEGS(self, segs: SEGS, control_net:
        CONTROL_NET, strength: float, start_percent: float, end_percent:
        float, segs_preprocessor: SEGS_PREPROCESSOR, control_image: IMAGE,
        vae: VAE) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'control_net': to_comfy_input(control_net), 'strength':
            to_comfy_input(strength), 'start_percent': to_comfy_input(
            start_percent), 'end_percent': to_comfy_input(end_percent),
            'segs_preprocessor': to_comfy_input(segs_preprocessor),
            'control_image': to_comfy_input(control_image), 'vae':
            to_comfy_input(vae)}, 'class_type':
            'ImpactControlNetApplyAdvancedSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactControlNetClearSEGS(self, segs: SEGS) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'ImpactControlNetClearSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactIPAdapterApplySEGS(self, segs: SEGS, ipadapter_pipe:
        IPADAPTER_PIPE, weight: float, noise: float, weight_type: str,
        start_at: float, end_at: float, unfold_batch: bool, faceid_v2: bool,
        weight_v2: float, context_crop_factor: float, reference_image:
        IMAGE, combine_embeds: str, neg_image: IMAGE) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'ipadapter_pipe': to_comfy_input(ipadapter_pipe), 'weight':
            to_comfy_input(weight), 'noise': to_comfy_input(noise),
            'weight_type': to_comfy_input(weight_type), 'start_at':
            to_comfy_input(start_at), 'end_at': to_comfy_input(end_at),
            'unfold_batch': to_comfy_input(unfold_batch), 'faceid_v2':
            to_comfy_input(faceid_v2), 'weight_v2': to_comfy_input(
            weight_v2), 'context_crop_factor': to_comfy_input(
            context_crop_factor), 'reference_image': to_comfy_input(
            reference_image), 'combine_embeds': to_comfy_input(
            combine_embeds), 'neg_image': to_comfy_input(neg_image)},
            'class_type': 'ImpactIPAdapterApplySEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactDecomposeSEGS(self, segs: SEGS) ->(SEGS_HEADER, SEG_ELT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'ImpactDecomposeSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS_HEADER(node_id, 0), SEG_ELT(node_id, 1)

    def ImpactAssembleSEGS(self, seg_header: SEGS_HEADER, seg_elt: SEG_ELT
        ) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seg_header': to_comfy_input(
            seg_header), 'seg_elt': to_comfy_input(seg_elt)}, 'class_type':
            'ImpactAssembleSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactFrom_SEG_ELT(self, seg_elt: SEG_ELT) ->(SEG_ELT, IMAGE, MASK,
        SEG_ELT_crop_region, SEG_ELT_bbox, SEG_ELT_control_net_wrapper,
        FloatNodeOutput, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seg_elt': to_comfy_input(seg_elt)},
            'class_type': 'ImpactFrom_SEG_ELT'}
        self._add_node(node_id, comfy_json_node)
        return SEG_ELT(node_id, 0), IMAGE(node_id, 1), MASK(node_id, 2
            ), SEG_ELT_crop_region(node_id, 3), SEG_ELT_bbox(node_id, 4
            ), SEG_ELT_control_net_wrapper(node_id, 5), FloatNodeOutput(node_id
            , 6), StrNodeOutput(node_id, 7)

    def ImpactEdit_SEG_ELT(self, seg_elt: SEG_ELT, cropped_image_opt: IMAGE,
        cropped_mask_opt: MASK, crop_region_opt: SEG_ELT_crop_region,
        bbox_opt: SEG_ELT_bbox, control_net_wrapper_opt:
        SEG_ELT_control_net_wrapper, confidence_opt: float, label_opt: str
        ) ->SEG_ELT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seg_elt': to_comfy_input(seg_elt),
            'cropped_image_opt': to_comfy_input(cropped_image_opt),
            'cropped_mask_opt': to_comfy_input(cropped_mask_opt),
            'crop_region_opt': to_comfy_input(crop_region_opt), 'bbox_opt':
            to_comfy_input(bbox_opt), 'control_net_wrapper_opt':
            to_comfy_input(control_net_wrapper_opt), 'confidence_opt':
            to_comfy_input(confidence_opt), 'label_opt': to_comfy_input(
            label_opt)}, 'class_type': 'ImpactEdit_SEG_ELT'}
        self._add_node(node_id, comfy_json_node)
        return SEG_ELT(node_id, 0)

    def ImpactDilate_Mask_SEG_ELT(self, seg_elt: SEG_ELT, dilation: int
        ) ->SEG_ELT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seg_elt': to_comfy_input(seg_elt),
            'dilation': to_comfy_input(dilation)}, 'class_type':
            'ImpactDilate_Mask_SEG_ELT'}
        self._add_node(node_id, comfy_json_node)
        return SEG_ELT(node_id, 0)

    def ImpactDilateMask(self, mask: MASK, dilation: int) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask),
            'dilation': to_comfy_input(dilation)}, 'class_type':
            'ImpactDilateMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImpactGaussianBlurMask(self, mask: MASK, kernel_size: int, sigma: float
        ) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask),
            'kernel_size': to_comfy_input(kernel_size), 'sigma':
            to_comfy_input(sigma)}, 'class_type': 'ImpactGaussianBlurMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImpactDilateMaskInSEGS(self, segs: SEGS, dilation: int) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'dilation': to_comfy_input(dilation)}, 'class_type':
            'ImpactDilateMaskInSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactGaussianBlurMaskInSEGS(self, segs: SEGS, kernel_size: int,
        sigma: float) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'kernel_size': to_comfy_input(kernel_size), 'sigma':
            to_comfy_input(sigma)}, 'class_type':
            'ImpactGaussianBlurMaskInSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactScaleBy_BBOX_SEG_ELT(self, seg: SEG_ELT, scale_by: float
        ) ->SEG_ELT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seg': to_comfy_input(seg),
            'scale_by': to_comfy_input(scale_by)}, 'class_type':
            'ImpactScaleBy_BBOX_SEG_ELT'}
        self._add_node(node_id, comfy_json_node)
        return SEG_ELT(node_id, 0)

    def ImpactFrom_SEG_ELT_bbox(self, bbox: SEG_ELT_bbox) ->(IntNodeOutput,
        IntNodeOutput, IntNodeOutput, IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'bbox': to_comfy_input(bbox)},
            'class_type': 'ImpactFrom_SEG_ELT_bbox'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0), IntNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2), IntNodeOutput(node_id, 3)

    def ImpactFrom_SEG_ELT_crop_region(self, crop_region: SEG_ELT_crop_region
        ) ->(IntNodeOutput, IntNodeOutput, IntNodeOutput, IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'crop_region': to_comfy_input(
            crop_region)}, 'class_type': 'ImpactFrom_SEG_ELT_crop_region'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0), IntNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2), IntNodeOutput(node_id, 3)

    def ImpactCount_Elts_in_SEGS(self, segs: SEGS) ->IntNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'ImpactCount_Elts_in_SEGS'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0)

    def BboxDetectorCombined_v2(self, bbox_detector: BBOX_DETECTOR, image:
        IMAGE, threshold: float, dilation: int) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'bbox_detector': to_comfy_input(
            bbox_detector), 'image': to_comfy_input(image), 'threshold':
            to_comfy_input(threshold), 'dilation': to_comfy_input(dilation)
            }, 'class_type': 'BboxDetectorCombined_v2'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def SegmDetectorCombined_v2(self, segm_detector: SEGM_DETECTOR, image:
        IMAGE, threshold: float, dilation: int) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segm_detector': to_comfy_input(
            segm_detector), 'image': to_comfy_input(image), 'threshold':
            to_comfy_input(threshold), 'dilation': to_comfy_input(dilation)
            }, 'class_type': 'SegmDetectorCombined_v2'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def SegsToCombinedMask(self, segs: SEGS) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'SegsToCombinedMask'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def KSamplerProvider(self, seed: int, steps: int, cfg: float,
        sampler_name: str, scheduler: str, denoise: float, basic_pipe:
        BASIC_PIPE, scheduler_func_opt: SCHEDULER_FUNC) ->KSAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'basic_pipe': to_comfy_input(basic_pipe), 'scheduler_func_opt':
            to_comfy_input(scheduler_func_opt)}, 'class_type':
            'KSamplerProvider'}
        self._add_node(node_id, comfy_json_node)
        return KSAMPLER(node_id, 0)

    def TwoSamplersForMask(self, latent_image: LATENT, base_sampler:
        KSAMPLER, mask_sampler: KSAMPLER, mask: MASK) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'latent_image': to_comfy_input(
            latent_image), 'base_sampler': to_comfy_input(base_sampler),
            'mask_sampler': to_comfy_input(mask_sampler), 'mask':
            to_comfy_input(mask)}, 'class_type': 'TwoSamplersForMask'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def TiledKSamplerProvider(self, seed: int, steps: int, cfg: float,
        sampler_name: str, scheduler: str, denoise: float, tile_width: int,
        tile_height: int, tiling_strategy: str, basic_pipe: BASIC_PIPE
        ) ->KSAMPLER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'tile_width': to_comfy_input(tile_width), 'tile_height':
            to_comfy_input(tile_height), 'tiling_strategy': to_comfy_input(
            tiling_strategy), 'basic_pipe': to_comfy_input(basic_pipe)},
            'class_type': 'TiledKSamplerProvider'}
        self._add_node(node_id, comfy_json_node)
        return KSAMPLER(node_id, 0)

    def KSamplerAdvancedProvider(self, cfg: float, sampler_name: str,
        scheduler: str, sigma_factor: float, basic_pipe: BASIC_PIPE,
        sampler_opt: SAMPLER, scheduler_func_opt: SCHEDULER_FUNC
        ) ->KSAMPLER_ADVANCED:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'sigma_factor': to_comfy_input(
            sigma_factor), 'basic_pipe': to_comfy_input(basic_pipe),
            'sampler_opt': to_comfy_input(sampler_opt),
            'scheduler_func_opt': to_comfy_input(scheduler_func_opt)},
            'class_type': 'KSamplerAdvancedProvider'}
        self._add_node(node_id, comfy_json_node)
        return KSAMPLER_ADVANCED(node_id, 0)

    def TwoAdvancedSamplersForMask(self, seed: int, steps: int, denoise:
        float, samples: LATENT, base_sampler: KSAMPLER_ADVANCED,
        mask_sampler: KSAMPLER_ADVANCED, mask: MASK, overlap_factor: int
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'denoise': to_comfy_input(denoise),
            'samples': to_comfy_input(samples), 'base_sampler':
            to_comfy_input(base_sampler), 'mask_sampler': to_comfy_input(
            mask_sampler), 'mask': to_comfy_input(mask), 'overlap_factor':
            to_comfy_input(overlap_factor)}, 'class_type':
            'TwoAdvancedSamplersForMask'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def ImpactNegativeConditioningPlaceholder(self) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {}, 'class_type':
            'ImpactNegativeConditioningPlaceholder'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def PreviewBridge(self, images: IMAGE, image: str, block: bool,
        restore_mask: str) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'image': to_comfy_input(image), 'block': to_comfy_input(block),
            'restore_mask': to_comfy_input(restore_mask)}, 'class_type':
            'PreviewBridge'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def PreviewBridgeLatent(self, latent: LATENT, image: str,
        preview_method: str, vae_opt: VAE, block: bool, restore_mask: str) ->(
        LATENT, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'latent': to_comfy_input(latent),
            'image': to_comfy_input(image), 'preview_method':
            to_comfy_input(preview_method), 'vae_opt': to_comfy_input(
            vae_opt), 'block': to_comfy_input(block), 'restore_mask':
            to_comfy_input(restore_mask)}, 'class_type': 'PreviewBridgeLatent'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0), MASK(node_id, 1)

    def ImageSender(self, images: IMAGE, filename_prefix: str, link_id: int
        ) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'filename_prefix': to_comfy_input(filename_prefix), 'link_id':
            to_comfy_input(link_id)}, 'class_type': 'ImageSender'}
        self._add_node(node_id, comfy_json_node)

    def ImageReceiver(self, image: str, link_id: int, save_to_workflow:
        bool, image_data: str, trigger_always: bool) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'link_id': to_comfy_input(link_id), 'save_to_workflow':
            to_comfy_input(save_to_workflow), 'image_data': to_comfy_input(
            image_data), 'trigger_always': to_comfy_input(trigger_always)},
            'class_type': 'ImageReceiver'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def LatentSender(self, samples: LATENT, filename_prefix: str, link_id:
        int, preview_method: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'filename_prefix': to_comfy_input(filename_prefix), 'link_id':
            to_comfy_input(link_id), 'preview_method': to_comfy_input(
            preview_method)}, 'class_type': 'LatentSender'}
        self._add_node(node_id, comfy_json_node)

    def LatentReceiver(self, latent: str, link_id: int, trigger_always: bool
        ) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'latent': to_comfy_input(latent),
            'link_id': to_comfy_input(link_id), 'trigger_always':
            to_comfy_input(trigger_always)}, 'class_type': 'LatentReceiver'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def ImageMaskSwitch(self, select: int, images1: IMAGE, mask1_opt: MASK,
        images2_opt: IMAGE, mask2_opt: MASK, images3_opt: IMAGE, mask3_opt:
        MASK, images4_opt: IMAGE, mask4_opt: MASK) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'select': to_comfy_input(select),
            'images1': to_comfy_input(images1), 'mask1_opt': to_comfy_input
            (mask1_opt), 'images2_opt': to_comfy_input(images2_opt),
            'mask2_opt': to_comfy_input(mask2_opt), 'images3_opt':
            to_comfy_input(images3_opt), 'mask3_opt': to_comfy_input(
            mask3_opt), 'images4_opt': to_comfy_input(images4_opt),
            'mask4_opt': to_comfy_input(mask4_opt)}, 'class_type':
            'ImageMaskSwitch'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def LatentSwitch(self, select: int, sel_mode: bool, input1: AnyNodeOutput
        ) ->(AnyNodeOutput, StrNodeOutput, IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'select': to_comfy_input(select),
            'sel_mode': to_comfy_input(sel_mode), 'input1': to_comfy_input(
            input1)}, 'class_type': 'LatentSwitch'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0), StrNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2)

    def SEGSSwitch(self, select: int, sel_mode: bool, input1: AnyNodeOutput
        ) ->(AnyNodeOutput, StrNodeOutput, IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'select': to_comfy_input(select),
            'sel_mode': to_comfy_input(sel_mode), 'input1': to_comfy_input(
            input1)}, 'class_type': 'SEGSSwitch'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0), StrNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2)

    def ImpactSwitch(self, select: int, sel_mode: bool, input1: AnyNodeOutput
        ) ->(AnyNodeOutput, StrNodeOutput, IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'select': to_comfy_input(select),
            'sel_mode': to_comfy_input(sel_mode), 'input1': to_comfy_input(
            input1)}, 'class_type': 'ImpactSwitch'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0), StrNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2)

    def ImpactInversedSwitch(self, select: int, input: AnyNodeOutput,
        sel_mode: bool) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'select': to_comfy_input(select),
            'input': to_comfy_input(input), 'sel_mode': to_comfy_input(
            sel_mode)}, 'class_type': 'ImpactInversedSwitch'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactWildcardProcessor(self, wildcard_text: str, populated_text:
        str, mode: str, seed: int, Select_to_add_Wildcard: str
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'wildcard_text': to_comfy_input(
            wildcard_text), 'populated_text': to_comfy_input(populated_text
            ), 'mode': to_comfy_input(mode), 'seed': to_comfy_input(seed),
            'Select to add Wildcard': to_comfy_input(Select_to_add_Wildcard
            )}, 'class_type': 'ImpactWildcardProcessor'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def ImpactWildcardEncode(self, model: MODEL, clip: CLIP, wildcard_text:
        str, populated_text: str, mode: str, Select_to_add_LoRA: str,
        Select_to_add_Wildcard: str, seed: int) ->(MODEL, CLIP,
        CONDITIONING, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'wildcard_text': to_comfy_input(
            wildcard_text), 'populated_text': to_comfy_input(populated_text
            ), 'mode': to_comfy_input(mode), 'Select to add LoRA':
            to_comfy_input(Select_to_add_LoRA), 'Select to add Wildcard':
            to_comfy_input(Select_to_add_Wildcard), 'seed': to_comfy_input(
            seed)}, 'class_type': 'ImpactWildcardEncode'}
        self._add_node(node_id, comfy_json_node)
        return MODEL(node_id, 0), CLIP(node_id, 1), CONDITIONING(node_id, 2
            ), StrNodeOutput(node_id, 3)

    def SEGSUpscaler(self, image: IMAGE, segs: SEGS, model: MODEL, clip:
        CLIP, vae: VAE, rescale_factor: float, resampling_method: str,
        supersample: str, rounding_modulus: int, seed: int, steps: int, cfg:
        float, sampler_name: str, scheduler: str, positive: CONDITIONING,
        negative: CONDITIONING, denoise: float, feather: int, inpaint_model:
        bool, noise_mask_feather: int, upscale_model_opt: UPSCALE_MODEL,
        upscaler_hook_opt: UPSCALER_HOOK, scheduler_func_opt: SCHEDULER_FUNC
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'model': to_comfy_input(model),
            'clip': to_comfy_input(clip), 'vae': to_comfy_input(vae),
            'rescale_factor': to_comfy_input(rescale_factor),
            'resampling_method': to_comfy_input(resampling_method),
            'supersample': to_comfy_input(supersample), 'rounding_modulus':
            to_comfy_input(rounding_modulus), 'seed': to_comfy_input(seed),
            'steps': to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'positive': to_comfy_input(positive),
            'negative': to_comfy_input(negative), 'denoise': to_comfy_input
            (denoise), 'feather': to_comfy_input(feather), 'inpaint_model':
            to_comfy_input(inpaint_model), 'noise_mask_feather':
            to_comfy_input(noise_mask_feather), 'upscale_model_opt':
            to_comfy_input(upscale_model_opt), 'upscaler_hook_opt':
            to_comfy_input(upscaler_hook_opt), 'scheduler_func_opt':
            to_comfy_input(scheduler_func_opt)}, 'class_type': 'SEGSUpscaler'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SEGSUpscalerPipe(self, image: IMAGE, segs: SEGS, basic_pipe:
        BASIC_PIPE, rescale_factor: float, resampling_method: str,
        supersample: str, rounding_modulus: int, seed: int, steps: int, cfg:
        float, sampler_name: str, scheduler: str, denoise: float, feather:
        int, inpaint_model: bool, noise_mask_feather: int,
        upscale_model_opt: UPSCALE_MODEL, upscaler_hook_opt: UPSCALER_HOOK,
        scheduler_func_opt: SCHEDULER_FUNC) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'basic_pipe': to_comfy_input(
            basic_pipe), 'rescale_factor': to_comfy_input(rescale_factor),
            'resampling_method': to_comfy_input(resampling_method),
            'supersample': to_comfy_input(supersample), 'rounding_modulus':
            to_comfy_input(rounding_modulus), 'seed': to_comfy_input(seed),
            'steps': to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'feather': to_comfy_input(feather), 'inpaint_model':
            to_comfy_input(inpaint_model), 'noise_mask_feather':
            to_comfy_input(noise_mask_feather), 'upscale_model_opt':
            to_comfy_input(upscale_model_opt), 'upscaler_hook_opt':
            to_comfy_input(upscaler_hook_opt), 'scheduler_func_opt':
            to_comfy_input(scheduler_func_opt)}, 'class_type':
            'SEGSUpscalerPipe'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SEGSDetailer(self, image: IMAGE, segs: SEGS, guide_size: float,
        guide_size_for: bool, max_size: float, seed: int, steps: int, cfg:
        float, sampler_name: str, scheduler: str, denoise: float,
        noise_mask: bool, force_inpaint: bool, basic_pipe: BASIC_PIPE,
        refiner_ratio: float, batch_size: int, cycle: int,
        refiner_basic_pipe_opt: BASIC_PIPE, inpaint_model: bool,
        noise_mask_feather: int, scheduler_func_opt: SCHEDULER_FUNC) ->(SEGS,
        IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'guide_size': to_comfy_input(
            guide_size), 'guide_size_for': to_comfy_input(guide_size_for),
            'max_size': to_comfy_input(max_size), 'seed': to_comfy_input(
            seed), 'steps': to_comfy_input(steps), 'cfg': to_comfy_input(
            cfg), 'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'denoise': to_comfy_input(denoise),
            'noise_mask': to_comfy_input(noise_mask), 'force_inpaint':
            to_comfy_input(force_inpaint), 'basic_pipe': to_comfy_input(
            basic_pipe), 'refiner_ratio': to_comfy_input(refiner_ratio),
            'batch_size': to_comfy_input(batch_size), 'cycle':
            to_comfy_input(cycle), 'refiner_basic_pipe_opt': to_comfy_input
            (refiner_basic_pipe_opt), 'inpaint_model': to_comfy_input(
            inpaint_model), 'noise_mask_feather': to_comfy_input(
            noise_mask_feather), 'scheduler_func_opt': to_comfy_input(
            scheduler_func_opt)}, 'class_type': 'SEGSDetailer'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0), IMAGE(node_id, 1)

    def SEGSPaste(self, image: IMAGE, segs: SEGS, feather: int, alpha: int,
        ref_image_opt: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'segs': to_comfy_input(segs), 'feather': to_comfy_input(feather
            ), 'alpha': to_comfy_input(alpha), 'ref_image_opt':
            to_comfy_input(ref_image_opt)}, 'class_type': 'SEGSPaste'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SEGSPreview(self, segs: SEGS, alpha_mode: bool, min_alpha: float,
        fallback_image_opt: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'alpha_mode': to_comfy_input(alpha_mode), 'min_alpha':
            to_comfy_input(min_alpha), 'fallback_image_opt': to_comfy_input
            (fallback_image_opt)}, 'class_type': 'SEGSPreview'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SEGSPreviewCNet(self, segs: SEGS) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'SEGSPreviewCNet'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SEGSToImageList(self, segs: SEGS, fallback_image_opt: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'fallback_image_opt': to_comfy_input(fallback_image_opt)},
            'class_type': 'SEGSToImageList'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImpactSEGSToMaskList(self, segs: SEGS) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'ImpactSEGSToMaskList'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImpactSEGSToMaskBatch(self, segs: SEGS) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'ImpactSEGSToMaskBatch'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImpactSEGSConcat(self, segs1: SEGS) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs1': to_comfy_input(segs1)},
            'class_type': 'ImpactSEGSConcat'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSEGSPicker(self, picks: str, segs: SEGS, fallback_image_opt:
        IMAGE) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'picks': to_comfy_input(picks),
            'segs': to_comfy_input(segs), 'fallback_image_opt':
            to_comfy_input(fallback_image_opt)}, 'class_type':
            'ImpactSEGSPicker'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactMakeTileSEGS(self, images: IMAGE, bbox_size: int, crop_factor:
        float, min_overlap: int, filter_segs_dilation: int,
        mask_irregularity: float, irregular_mask_mode: str,
        filter_in_segs_opt: SEGS, filter_out_segs_opt: SEGS) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'images': to_comfy_input(images),
            'bbox_size': to_comfy_input(bbox_size), 'crop_factor':
            to_comfy_input(crop_factor), 'min_overlap': to_comfy_input(
            min_overlap), 'filter_segs_dilation': to_comfy_input(
            filter_segs_dilation), 'mask_irregularity': to_comfy_input(
            mask_irregularity), 'irregular_mask_mode': to_comfy_input(
            irregular_mask_mode), 'filter_in_segs_opt': to_comfy_input(
            filter_in_segs_opt), 'filter_out_segs_opt': to_comfy_input(
            filter_out_segs_opt)}, 'class_type': 'ImpactMakeTileSEGS'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSEGSMerge(self, segs: SEGS) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'ImpactSEGSMerge'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def SEGSDetailerForAnimateDiff(self, image_frames: IMAGE, segs: SEGS,
        guide_size: float, guide_size_for: bool, max_size: float, seed: int,
        steps: int, cfg: float, sampler_name: str, scheduler: str, denoise:
        float, basic_pipe: BASIC_PIPE, refiner_ratio: float,
        refiner_basic_pipe_opt: BASIC_PIPE, noise_mask_feather: int,
        scheduler_func_opt: SCHEDULER_FUNC) ->(SEGS, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image_frames': to_comfy_input(
            image_frames), 'segs': to_comfy_input(segs), 'guide_size':
            to_comfy_input(guide_size), 'guide_size_for': to_comfy_input(
            guide_size_for), 'max_size': to_comfy_input(max_size), 'seed':
            to_comfy_input(seed), 'steps': to_comfy_input(steps), 'cfg':
            to_comfy_input(cfg), 'sampler_name': to_comfy_input(
            sampler_name), 'scheduler': to_comfy_input(scheduler),
            'denoise': to_comfy_input(denoise), 'basic_pipe':
            to_comfy_input(basic_pipe), 'refiner_ratio': to_comfy_input(
            refiner_ratio), 'refiner_basic_pipe_opt': to_comfy_input(
            refiner_basic_pipe_opt), 'noise_mask_feather': to_comfy_input(
            noise_mask_feather), 'scheduler_func_opt': to_comfy_input(
            scheduler_func_opt)}, 'class_type': 'SEGSDetailerForAnimateDiff'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0), IMAGE(node_id, 1)

    def ImpactKSamplerBasicPipe(self, basic_pipe: BASIC_PIPE, seed: int,
        steps: int, cfg: float, sampler_name: str, scheduler: str,
        latent_image: LATENT, denoise: float, scheduler_func_opt:
        SCHEDULER_FUNC) ->(BASIC_PIPE, LATENT, VAE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'basic_pipe': to_comfy_input(
            basic_pipe), 'seed': to_comfy_input(seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'latent_image': to_comfy_input(
            latent_image), 'denoise': to_comfy_input(denoise),
            'scheduler_func_opt': to_comfy_input(scheduler_func_opt)},
            'class_type': 'ImpactKSamplerBasicPipe'}
        self._add_node(node_id, comfy_json_node)
        return BASIC_PIPE(node_id, 0), LATENT(node_id, 1), VAE(node_id, 2)

    def ImpactKSamplerAdvancedBasicPipe(self, basic_pipe: BASIC_PIPE,
        add_noise: bool, noise_seed: int, steps: int, cfg: float,
        sampler_name: str, scheduler: str, latent_image: LATENT,
        start_at_step: int, end_at_step: int, return_with_leftover_noise:
        bool, scheduler_func_opt: SCHEDULER_FUNC) ->(BASIC_PIPE, LATENT, VAE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'basic_pipe': to_comfy_input(
            basic_pipe), 'add_noise': to_comfy_input(add_noise),
            'noise_seed': to_comfy_input(noise_seed), 'steps':
            to_comfy_input(steps), 'cfg': to_comfy_input(cfg),
            'sampler_name': to_comfy_input(sampler_name), 'scheduler':
            to_comfy_input(scheduler), 'latent_image': to_comfy_input(
            latent_image), 'start_at_step': to_comfy_input(start_at_step),
            'end_at_step': to_comfy_input(end_at_step),
            'return_with_leftover_noise': to_comfy_input(
            return_with_leftover_noise), 'scheduler_func_opt':
            to_comfy_input(scheduler_func_opt)}, 'class_type':
            'ImpactKSamplerAdvancedBasicPipe'}
        self._add_node(node_id, comfy_json_node)
        return BASIC_PIPE(node_id, 0), LATENT(node_id, 1), VAE(node_id, 2)

    def ReencodeLatent(self, samples: LATENT, tile_mode: str, input_vae:
        VAE, output_vae: VAE, tile_size: int, overlap: int) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'tile_mode': to_comfy_input(tile_mode), 'input_vae':
            to_comfy_input(input_vae), 'output_vae': to_comfy_input(
            output_vae), 'tile_size': to_comfy_input(tile_size), 'overlap':
            to_comfy_input(overlap)}, 'class_type': 'ReencodeLatent'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def ReencodeLatentPipe(self, samples: LATENT, tile_mode: str,
        input_basic_pipe: BASIC_PIPE, output_basic_pipe: BASIC_PIPE) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples),
            'tile_mode': to_comfy_input(tile_mode), 'input_basic_pipe':
            to_comfy_input(input_basic_pipe), 'output_basic_pipe':
            to_comfy_input(output_basic_pipe)}, 'class_type':
            'ReencodeLatentPipe'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def ImpactImageBatchToImageList(self, image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'ImpactImageBatchToImageList'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImpactMakeImageList(self, image1: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image1': to_comfy_input(image1)},
            'class_type': 'ImpactMakeImageList'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImpactMakeImageBatch(self, image1: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image1': to_comfy_input(image1)},
            'class_type': 'ImpactMakeImageBatch'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImpactMakeAnyList(self, value1: AnyNodeOutput) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value1': to_comfy_input(value1)},
            'class_type': 'ImpactMakeAnyList'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactMakeMaskList(self, mask1: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask1': to_comfy_input(mask1)},
            'class_type': 'ImpactMakeMaskList'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImpactMakeMaskBatch(self, mask1: MASK) ->MASK:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask1': to_comfy_input(mask1)},
            'class_type': 'ImpactMakeMaskBatch'}
        self._add_node(node_id, comfy_json_node)
        return MASK(node_id, 0)

    def ImpactSelectNthItemOfAnyList(self, any_list: AnyNodeOutput, index: int
        ) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'any_list': to_comfy_input(any_list),
            'index': to_comfy_input(index)}, 'class_type':
            'ImpactSelectNthItemOfAnyList'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def RegionalSampler(self, seed: int, seed_2nd: int, seed_2nd_mode: str,
        steps: int, base_only_steps: int, denoise: float, samples: LATENT,
        base_sampler: KSAMPLER_ADVANCED, regional_prompts: REGIONAL_PROMPTS,
        overlap_factor: int, restore_latent: bool, additional_mode: str,
        additional_sampler: str, additional_sigma_ratio: float) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'seed': to_comfy_input(seed),
            'seed_2nd': to_comfy_input(seed_2nd), 'seed_2nd_mode':
            to_comfy_input(seed_2nd_mode), 'steps': to_comfy_input(steps),
            'base_only_steps': to_comfy_input(base_only_steps), 'denoise':
            to_comfy_input(denoise), 'samples': to_comfy_input(samples),
            'base_sampler': to_comfy_input(base_sampler),
            'regional_prompts': to_comfy_input(regional_prompts),
            'overlap_factor': to_comfy_input(overlap_factor),
            'restore_latent': to_comfy_input(restore_latent),
            'additional_mode': to_comfy_input(additional_mode),
            'additional_sampler': to_comfy_input(additional_sampler),
            'additional_sigma_ratio': to_comfy_input(additional_sigma_ratio
            )}, 'class_type': 'RegionalSampler'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def RegionalSamplerAdvanced(self, add_noise: bool, noise_seed: int,
        steps: int, start_at_step: int, end_at_step: int, overlap_factor:
        int, restore_latent: bool, return_with_leftover_noise: bool,
        latent_image: LATENT, base_sampler: KSAMPLER_ADVANCED,
        regional_prompts: REGIONAL_PROMPTS, additional_mode: str,
        additional_sampler: str, additional_sigma_ratio: float) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'add_noise': to_comfy_input(add_noise
            ), 'noise_seed': to_comfy_input(noise_seed), 'steps':
            to_comfy_input(steps), 'start_at_step': to_comfy_input(
            start_at_step), 'end_at_step': to_comfy_input(end_at_step),
            'overlap_factor': to_comfy_input(overlap_factor),
            'restore_latent': to_comfy_input(restore_latent),
            'return_with_leftover_noise': to_comfy_input(
            return_with_leftover_noise), 'latent_image': to_comfy_input(
            latent_image), 'base_sampler': to_comfy_input(base_sampler),
            'regional_prompts': to_comfy_input(regional_prompts),
            'additional_mode': to_comfy_input(additional_mode),
            'additional_sampler': to_comfy_input(additional_sampler),
            'additional_sigma_ratio': to_comfy_input(additional_sigma_ratio
            )}, 'class_type': 'RegionalSamplerAdvanced'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def CombineRegionalPrompts(self, regional_prompts1: REGIONAL_PROMPTS
        ) ->REGIONAL_PROMPTS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'regional_prompts1': to_comfy_input(
            regional_prompts1)}, 'class_type': 'CombineRegionalPrompts'}
        self._add_node(node_id, comfy_json_node)
        return REGIONAL_PROMPTS(node_id, 0)

    def RegionalPrompt(self, mask: MASK, advanced_sampler:
        KSAMPLER_ADVANCED, variation_seed: int, variation_strength: float,
        variation_method: str) ->REGIONAL_PROMPTS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mask': to_comfy_input(mask),
            'advanced_sampler': to_comfy_input(advanced_sampler),
            'variation_seed': to_comfy_input(variation_seed),
            'variation_strength': to_comfy_input(variation_strength),
            'variation_method': to_comfy_input(variation_method)},
            'class_type': 'RegionalPrompt'}
        self._add_node(node_id, comfy_json_node)
        return REGIONAL_PROMPTS(node_id, 0)

    def ImpactCombineConditionings(self, conditioning1: CONDITIONING
        ) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning1': to_comfy_input(
            conditioning1)}, 'class_type': 'ImpactCombineConditionings'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ImpactConcatConditionings(self, conditioning1: CONDITIONING
        ) ->CONDITIONING:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'conditioning1': to_comfy_input(
            conditioning1)}, 'class_type': 'ImpactConcatConditionings'}
        self._add_node(node_id, comfy_json_node)
        return CONDITIONING(node_id, 0)

    def ImpactSEGSLabelAssign(self, segs: SEGS, labels: str) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'labels': to_comfy_input(labels)}, 'class_type':
            'ImpactSEGSLabelAssign'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSEGSLabelFilter(self, segs: SEGS, preset: str, labels: str) ->(
        SEGS, SEGS):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'preset': to_comfy_input(preset), 'labels': to_comfy_input(
            labels)}, 'class_type': 'ImpactSEGSLabelFilter'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0), SEGS(node_id, 1)

    def ImpactSEGSRangeFilter(self, segs: SEGS, target: str, mode: bool,
        min_value: int, max_value: int) ->(SEGS, SEGS):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'target': to_comfy_input(target), 'mode': to_comfy_input(mode),
            'min_value': to_comfy_input(min_value), 'max_value':
            to_comfy_input(max_value)}, 'class_type': 'ImpactSEGSRangeFilter'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0), SEGS(node_id, 1)

    def ImpactSEGSOrderedFilter(self, segs: SEGS, target: str, order: bool,
        take_start: int, take_count: int) ->(SEGS, SEGS):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'target': to_comfy_input(target), 'order': to_comfy_input(order
            ), 'take_start': to_comfy_input(take_start), 'take_count':
            to_comfy_input(take_count)}, 'class_type':
            'ImpactSEGSOrderedFilter'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0), SEGS(node_id, 1)

    def ImpactSEGSIntersectionFilter(self, segs1: SEGS, segs2: SEGS,
        ioa_threshold: float) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs1': to_comfy_input(segs1),
            'segs2': to_comfy_input(segs2), 'ioa_threshold': to_comfy_input
            (ioa_threshold)}, 'class_type': 'ImpactSEGSIntersectionFilter'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactSEGSNMSFilter(self, segs: SEGS, iou_threshold: float) ->SEGS:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs),
            'iou_threshold': to_comfy_input(iou_threshold)}, 'class_type':
            'ImpactSEGSNMSFilter'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0)

    def ImpactCompare(self, cmp: str, a: AnyNodeOutput, b: AnyNodeOutput
        ) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'cmp': to_comfy_input(cmp), 'a':
            to_comfy_input(a), 'b': to_comfy_input(b)}, 'class_type':
            'ImpactCompare'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def ImpactConditionalBranch(self, cond: bool, tt_value: AnyNodeOutput,
        ff_value: AnyNodeOutput) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'cond': to_comfy_input(cond),
            'tt_value': to_comfy_input(tt_value), 'ff_value':
            to_comfy_input(ff_value)}, 'class_type': 'ImpactConditionalBranch'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactConditionalBranchSelMode(self, cond: bool, tt_value:
        AnyNodeOutput, ff_value: AnyNodeOutput) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'cond': to_comfy_input(cond),
            'tt_value': to_comfy_input(tt_value), 'ff_value':
            to_comfy_input(ff_value)}, 'class_type':
            'ImpactConditionalBranchSelMode'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactIfNone(self, signal: AnyNodeOutput, any_input: AnyNodeOutput) ->(
        AnyNodeOutput, BoolNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'signal': to_comfy_input(signal),
            'any_input': to_comfy_input(any_input)}, 'class_type':
            'ImpactIfNone'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0), BoolNodeOutput(node_id, 1)

    def ImpactConvertDataType(self, value: AnyNodeOutput) ->(StrNodeOutput,
        FloatNodeOutput, IntNodeOutput, BoolNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'ImpactConvertDataType'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), FloatNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2), BoolNodeOutput(node_id, 3)

    def ImpactLogicalOperators(self, operator: str, bool_a: bool, bool_b: bool
        ) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'operator': to_comfy_input(operator),
            'bool_a': to_comfy_input(bool_a), 'bool_b': to_comfy_input(
            bool_b)}, 'class_type': 'ImpactLogicalOperators'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def ImpactInt(self, value: int) ->IntNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'ImpactInt'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0)

    def ImpactFloat(self, value: float) ->FloatNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'ImpactFloat'}
        self._add_node(node_id, comfy_json_node)
        return FloatNodeOutput(node_id, 0)

    def ImpactBoolean(self, value: bool) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'ImpactBoolean'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def ImpactValueSender(self, value: AnyNodeOutput, link_id: int,
        signal_opt: AnyNodeOutput) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value),
            'link_id': to_comfy_input(link_id), 'signal_opt':
            to_comfy_input(signal_opt)}, 'class_type': 'ImpactValueSender'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactValueReceiver(self, typ: str, value: str, link_id: int
        ) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'typ': to_comfy_input(typ), 'value':
            to_comfy_input(value), 'link_id': to_comfy_input(link_id)},
            'class_type': 'ImpactValueReceiver'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactImageInfo(self, value: IMAGE) ->(IntNodeOutput, IntNodeOutput,
        IntNodeOutput, IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'ImpactImageInfo'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0), IntNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2), IntNodeOutput(node_id, 3)

    def ImpactLatentInfo(self, value: LATENT) ->(IntNodeOutput,
        IntNodeOutput, IntNodeOutput, IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'ImpactLatentInfo'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0), IntNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2), IntNodeOutput(node_id, 3)

    def ImpactMinMax(self, mode: bool, a: AnyNodeOutput, b: AnyNodeOutput
        ) ->IntNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'mode': to_comfy_input(mode), 'a':
            to_comfy_input(a), 'b': to_comfy_input(b)}, 'class_type':
            'ImpactMinMax'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0)

    def ImpactNeg(self, value: bool) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value)},
            'class_type': 'ImpactNeg'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def ImpactConditionalStopIteration(self, cond: bool) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'cond': to_comfy_input(cond)},
            'class_type': 'ImpactConditionalStopIteration'}
        self._add_node(node_id, comfy_json_node)

    def ImpactStringSelector(self, strings: str, multiline: bool, select: int
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'strings': to_comfy_input(strings),
            'multiline': to_comfy_input(multiline), 'select':
            to_comfy_input(select)}, 'class_type': 'ImpactStringSelector'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def StringListToString(self, join_with: str, string_list: str
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'join_with': to_comfy_input(join_with
            ), 'string_list': to_comfy_input(string_list)}, 'class_type':
            'StringListToString'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def WildcardPromptFromString(self, string: str, delimiter: str,
        prefix_all: str, postfix_all: str, restrict_to_tags: str,
        exclude_tags: str) ->(StrNodeOutput, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'string': to_comfy_input(string),
            'delimiter': to_comfy_input(delimiter), 'prefix_all':
            to_comfy_input(prefix_all), 'postfix_all': to_comfy_input(
            postfix_all), 'restrict_to_tags': to_comfy_input(
            restrict_to_tags), 'exclude_tags': to_comfy_input(exclude_tags)
            }, 'class_type': 'WildcardPromptFromString'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0), StrNodeOutput(node_id, 1)

    def ImpactExecutionOrderController(self, signal: AnyNodeOutput, value:
        AnyNodeOutput) ->(AnyNodeOutput, AnyNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'signal': to_comfy_input(signal),
            'value': to_comfy_input(value)}, 'class_type':
            'ImpactExecutionOrderController'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0), AnyNodeOutput(node_id, 1)

    def ImpactListBridge(self, list_input: AnyNodeOutput) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'list_input': to_comfy_input(
            list_input)}, 'class_type': 'ImpactListBridge'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def RemoveNoiseMask(self, samples: LATENT) ->LATENT:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'samples': to_comfy_input(samples)},
            'class_type': 'RemoveNoiseMask'}
        self._add_node(node_id, comfy_json_node)
        return LATENT(node_id, 0)

    def ImpactLogger(self, data: AnyNodeOutput, text: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'data': to_comfy_input(data), 'text':
            to_comfy_input(text)}, 'class_type': 'ImpactLogger'}
        self._add_node(node_id, comfy_json_node)

    def ImpactDummyInput(self) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {}, 'class_type': 'ImpactDummyInput'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactQueueTrigger(self, signal: AnyNodeOutput, mode: bool
        ) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'signal': to_comfy_input(signal),
            'mode': to_comfy_input(mode)}, 'class_type': 'ImpactQueueTrigger'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactQueueTriggerCountdown(self, count: int, total: int, mode:
        bool, signal: AnyNodeOutput) ->(AnyNodeOutput, IntNodeOutput,
        IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'count': to_comfy_input(count),
            'total': to_comfy_input(total), 'mode': to_comfy_input(mode),
            'signal': to_comfy_input(signal)}, 'class_type':
            'ImpactQueueTriggerCountdown'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0), IntNodeOutput(node_id, 1
            ), IntNodeOutput(node_id, 2)

    def ImpactSetWidgetValue(self, signal: AnyNodeOutput, node_id: int,
        widget_name: str, boolean_value: bool, int_value: int, float_value:
        float, string_value: str) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'signal': to_comfy_input(signal),
            'node_id': to_comfy_input(node_id), 'widget_name':
            to_comfy_input(widget_name), 'boolean_value': to_comfy_input(
            boolean_value), 'int_value': to_comfy_input(int_value),
            'float_value': to_comfy_input(float_value), 'string_value':
            to_comfy_input(string_value)}, 'class_type': 'ImpactSetWidgetValue'
            }
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactNodeSetMuteState(self, signal: AnyNodeOutput, node_id: int,
        set_state: bool) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'signal': to_comfy_input(signal),
            'node_id': to_comfy_input(node_id), 'set_state': to_comfy_input
            (set_state)}, 'class_type': 'ImpactNodeSetMuteState'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactControlBridge(self, value: AnyNodeOutput, mode: bool,
        behavior: str) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'value': to_comfy_input(value),
            'mode': to_comfy_input(mode), 'behavior': to_comfy_input(
            behavior)}, 'class_type': 'ImpactControlBridge'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactIsNotEmptySEGS(self, segs: SEGS) ->BoolNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'segs': to_comfy_input(segs)},
            'class_type': 'ImpactIsNotEmptySEGS'}
        self._add_node(node_id, comfy_json_node)
        return BoolNodeOutput(node_id, 0)

    def ImpactSleep(self, signal: AnyNodeOutput, seconds: float
        ) ->AnyNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'signal': to_comfy_input(signal),
            'seconds': to_comfy_input(seconds)}, 'class_type': 'ImpactSleep'}
        self._add_node(node_id, comfy_json_node)
        return AnyNodeOutput(node_id, 0)

    def ImpactRemoteBoolean(self, node_id: int, widget_name: str, value: bool
        ) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'node_id': to_comfy_input(node_id),
            'widget_name': to_comfy_input(widget_name), 'value':
            to_comfy_input(value)}, 'class_type': 'ImpactRemoteBoolean'}
        self._add_node(node_id, comfy_json_node)

    def ImpactRemoteInt(self, node_id: int, widget_name: str, value: int
        ) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'node_id': to_comfy_input(node_id),
            'widget_name': to_comfy_input(widget_name), 'value':
            to_comfy_input(value)}, 'class_type': 'ImpactRemoteInt'}
        self._add_node(node_id, comfy_json_node)

    def ImpactHFTransformersClassifierProvider(self, preset_repo_id: str,
        manual_repo_id: str, device_mode: str) ->TRANSFORMERS_CLASSIFIER:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'preset_repo_id': to_comfy_input(
            preset_repo_id), 'manual_repo_id': to_comfy_input(
            manual_repo_id), 'device_mode': to_comfy_input(device_mode)},
            'class_type': 'ImpactHFTransformersClassifierProvider'}
        self._add_node(node_id, comfy_json_node)
        return TRANSFORMERS_CLASSIFIER(node_id, 0)

    def ImpactSEGSClassify(self, classifier: TRANSFORMERS_CLASSIFIER, segs:
        SEGS, preset_expr: str, manual_expr: str, ref_image_opt: IMAGE) ->(SEGS
        , SEGS, StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'classifier': to_comfy_input(
            classifier), 'segs': to_comfy_input(segs), 'preset_expr':
            to_comfy_input(preset_expr), 'manual_expr': to_comfy_input(
            manual_expr), 'ref_image_opt': to_comfy_input(ref_image_opt)},
            'class_type': 'ImpactSEGSClassify'}
        self._add_node(node_id, comfy_json_node)
        return SEGS(node_id, 0), SEGS(node_id, 1), StrNodeOutput(node_id, 2)

    def ImpactSchedulerAdapter(self, scheduler: str, extra_scheduler: str
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'scheduler': to_comfy_input(scheduler
            ), 'extra_scheduler': to_comfy_input(extra_scheduler)},
            'class_type': 'ImpactSchedulerAdapter'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def GITSSchedulerFuncProvider(self, coeff: float, denoise: float
        ) ->SCHEDULER_FUNC:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'coeff': to_comfy_input(coeff),
            'denoise': to_comfy_input(denoise)}, 'class_type':
            'GITSSchedulerFuncProvider'}
        self._add_node(node_id, comfy_json_node)
        return SCHEDULER_FUNC(node_id, 0)

    def AddRandomArtists(self, prompt: str, num_artists: int,
        min_post_count: int, weight_noise: float, seed: int) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'prompt': to_comfy_input(prompt),
            'num_artists': to_comfy_input(num_artists), 'min_post_count':
            to_comfy_input(min_post_count), 'weight_noise': to_comfy_input(
            weight_noise), 'seed': to_comfy_input(seed)}, 'class_type':
            'AddRandomArtists'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def TextInput(self, text: str) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'text': to_comfy_input(text)},
            'class_type': 'TextInput'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def UniFormer_SemSegPreprocessor(self, image: IMAGE, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'UniFormer-SemSegPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SemSegPreprocessor(self, image: IMAGE, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'SemSegPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SAMPreprocessor(self, image: IMAGE, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'SAMPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DepthAnythingV2Preprocessor(self, image: IMAGE, ckpt_name: str,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'ckpt_name': to_comfy_input(ckpt_name), 'resolution':
            to_comfy_input(resolution)}, 'class_type':
            'DepthAnythingV2Preprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def OneFormer_COCO_SemSegPreprocessor(self, image: IMAGE, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'OneFormer-COCO-SemSegPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def OneFormer_ADE20K_SemSegPreprocessor(self, image: IMAGE, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'OneFormer-ADE20K-SemSegPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def MeshGraphormer_DepthMapPreprocessor(self, image: IMAGE,
        mask_bbox_padding: int, resolution: int, mask_type: str,
        mask_expand: int, rand_seed: int, detect_thr: float, presence_thr:
        float) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'mask_bbox_padding': to_comfy_input(mask_bbox_padding),
            'resolution': to_comfy_input(resolution), 'mask_type':
            to_comfy_input(mask_type), 'mask_expand': to_comfy_input(
            mask_expand), 'rand_seed': to_comfy_input(rand_seed),
            'detect_thr': to_comfy_input(detect_thr), 'presence_thr':
            to_comfy_input(presence_thr)}, 'class_type':
            'MeshGraphormer-DepthMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def MeshGraphormer_ImpactDetector_DepthMapPreprocessor(self, image:
        IMAGE, bbox_detector: BBOX_DETECTOR, bbox_threshold: float,
        bbox_dilation: int, bbox_crop_factor: float, drop_size: int,
        mask_bbox_padding: int, mask_type: str, mask_expand: int, rand_seed:
        int, resolution: int) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'bbox_detector': to_comfy_input(bbox_detector),
            'bbox_threshold': to_comfy_input(bbox_threshold),
            'bbox_dilation': to_comfy_input(bbox_dilation),
            'bbox_crop_factor': to_comfy_input(bbox_crop_factor),
            'drop_size': to_comfy_input(drop_size), 'mask_bbox_padding':
            to_comfy_input(mask_bbox_padding), 'mask_type': to_comfy_input(
            mask_type), 'mask_expand': to_comfy_input(mask_expand),
            'rand_seed': to_comfy_input(rand_seed), 'resolution':
            to_comfy_input(resolution)}, 'class_type':
            'MeshGraphormer+ImpactDetector-DepthMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def LineArtPreprocessor(self, image: IMAGE, coarse: str, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'coarse': to_comfy_input(coarse), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'LineArtPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def HEDPreprocessor(self, image: IMAGE, safe: str, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'safe': to_comfy_input(safe), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'HEDPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def FakeScribblePreprocessor(self, image: IMAGE, safe: str, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'safe': to_comfy_input(safe), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'FakeScribblePreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LeReS_DepthMapPreprocessor(self, image: IMAGE, rm_nearest: float,
        rm_background: float, boost: str, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'rm_nearest': to_comfy_input(rm_nearest), 'rm_background':
            to_comfy_input(rm_background), 'boost': to_comfy_input(boost),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'LeReS-DepthMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def AnimeLineArtPreprocessor(self, image: IMAGE, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'AnimeLineArtPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def CannyEdgePreprocessor(self, image: IMAGE, low_threshold: int,
        high_threshold: int, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'low_threshold': to_comfy_input(low_threshold),
            'high_threshold': to_comfy_input(high_threshold), 'resolution':
            to_comfy_input(resolution)}, 'class_type': 'CannyEdgePreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ColorPreprocessor(self, image: IMAGE, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'ColorPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def MiDaS_NormalMapPreprocessor(self, image: IMAGE, a: float,
        bg_threshold: float, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image), 'a':
            to_comfy_input(a), 'bg_threshold': to_comfy_input(bg_threshold),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'MiDaS-NormalMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def MiDaS_DepthMapPreprocessor(self, image: IMAGE, a: float,
        bg_threshold: float, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image), 'a':
            to_comfy_input(a), 'bg_threshold': to_comfy_input(bg_threshold),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'MiDaS-DepthMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Metric3D_DepthMapPreprocessor(self, image: IMAGE, backbone: str, fx:
        int, fy: int, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'backbone': to_comfy_input(backbone), 'fx': to_comfy_input(fx),
            'fy': to_comfy_input(fy), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'Metric3D-DepthMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Metric3D_NormalMapPreprocessor(self, image: IMAGE, backbone: str,
        fx: int, fy: int, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'backbone': to_comfy_input(backbone), 'fx': to_comfy_input(fx),
            'fy': to_comfy_input(fy), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'Metric3D-NormalMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def PiDiNetPreprocessor(self, image: IMAGE, safe: str, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'safe': to_comfy_input(safe), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'PiDiNetPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DiffusionEdge_Preprocessor(self, image: IMAGE, environment: str,
        patch_batch_size: int, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'environment': to_comfy_input(environment), 'patch_batch_size':
            to_comfy_input(patch_batch_size), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'DiffusionEdge_Preprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def OpenposePreprocessor(self, image: IMAGE, detect_hand: str,
        detect_body: str, detect_face: str, resolution: int,
        scale_stick_for_xinsr_cn: str) ->(IMAGE, POSE_KEYPOINT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'detect_hand': to_comfy_input(detect_hand), 'detect_body':
            to_comfy_input(detect_body), 'detect_face': to_comfy_input(
            detect_face), 'resolution': to_comfy_input(resolution),
            'scale_stick_for_xinsr_cn': to_comfy_input(
            scale_stick_for_xinsr_cn)}, 'class_type': 'OpenposePreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), POSE_KEYPOINT(node_id, 1)

    def PyraCannyPreprocessor(self, image: IMAGE, low_threshold: int,
        high_threshold: int, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'low_threshold': to_comfy_input(low_threshold),
            'high_threshold': to_comfy_input(high_threshold), 'resolution':
            to_comfy_input(resolution)}, 'class_type': 'PyraCannyPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DWPreprocessor(self, image: IMAGE, detect_hand: str, detect_body:
        str, detect_face: str, resolution: int, bbox_detector: str,
        pose_estimator: str, scale_stick_for_xinsr_cn: str) ->(IMAGE,
        POSE_KEYPOINT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'detect_hand': to_comfy_input(detect_hand), 'detect_body':
            to_comfy_input(detect_body), 'detect_face': to_comfy_input(
            detect_face), 'resolution': to_comfy_input(resolution),
            'bbox_detector': to_comfy_input(bbox_detector),
            'pose_estimator': to_comfy_input(pose_estimator),
            'scale_stick_for_xinsr_cn': to_comfy_input(
            scale_stick_for_xinsr_cn)}, 'class_type': 'DWPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), POSE_KEYPOINT(node_id, 1)

    def AnimalPosePreprocessor(self, image: IMAGE, bbox_detector: str,
        pose_estimator: str, resolution: int) ->(IMAGE, POSE_KEYPOINT):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'bbox_detector': to_comfy_input(bbox_detector),
            'pose_estimator': to_comfy_input(pose_estimator), 'resolution':
            to_comfy_input(resolution)}, 'class_type': 'AnimalPosePreprocessor'
            }
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), POSE_KEYPOINT(node_id, 1)

    def BinaryPreprocessor(self, image: IMAGE, bin_threshold: int,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'bin_threshold': to_comfy_input(bin_threshold), 'resolution':
            to_comfy_input(resolution)}, 'class_type': 'BinaryPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Manga2Anime_LineArt_Preprocessor(self, image: IMAGE, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'Manga2Anime_LineArt_Preprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def BAE_NormalMapPreprocessor(self, image: IMAGE, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'BAE-NormalMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DepthAnythingPreprocessor(self, image: IMAGE, ckpt_name: str,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'ckpt_name': to_comfy_input(ckpt_name), 'resolution':
            to_comfy_input(resolution)}, 'class_type':
            'DepthAnythingPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Zoe_DepthAnythingPreprocessor(self, image: IMAGE, environment: str,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'environment': to_comfy_input(environment), 'resolution':
            to_comfy_input(resolution)}, 'class_type':
            'Zoe_DepthAnythingPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def M_LSDPreprocessor(self, image: IMAGE, score_threshold: float,
        dist_threshold: float, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'score_threshold': to_comfy_input(score_threshold),
            'dist_threshold': to_comfy_input(dist_threshold), 'resolution':
            to_comfy_input(resolution)}, 'class_type': 'M-LSDPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def TilePreprocessor(self, image: IMAGE, pyrUp_iters: int, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'pyrUp_iters': to_comfy_input(pyrUp_iters), 'resolution':
            to_comfy_input(resolution)}, 'class_type': 'TilePreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def TTPlanet_TileGF_Preprocessor(self, image: IMAGE, scale_factor:
        float, blur_strength: float, radius: int, eps: float, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'scale_factor': to_comfy_input(scale_factor), 'blur_strength':
            to_comfy_input(blur_strength), 'radius': to_comfy_input(radius),
            'eps': to_comfy_input(eps), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'TTPlanet_TileGF_Preprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def TTPlanet_TileSimple_Preprocessor(self, image: IMAGE, scale_factor:
        float, blur_strength: float) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'scale_factor': to_comfy_input(scale_factor), 'blur_strength':
            to_comfy_input(blur_strength)}, 'class_type':
            'TTPlanet_TileSimple_Preprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def AnimeFace_SemSegPreprocessor(self, image: IMAGE,
        remove_background_using_abg: bool, resolution: int) ->(IMAGE, MASK):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'remove_background_using_abg': to_comfy_input(
            remove_background_using_abg), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'AnimeFace_SemSegPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0), MASK(node_id, 1)

    def AnyLineArtPreprocessor_aux(self, image: IMAGE, merge_with_lineart:
        str, resolution: int, lineart_lower_bound: float,
        lineart_upper_bound: float, object_min_size: int,
        object_connectivity: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'merge_with_lineart': to_comfy_input(merge_with_lineart),
            'resolution': to_comfy_input(resolution), 'lineart_lower_bound':
            to_comfy_input(lineart_lower_bound), 'lineart_upper_bound':
            to_comfy_input(lineart_upper_bound), 'object_min_size':
            to_comfy_input(object_min_size), 'object_connectivity':
            to_comfy_input(object_connectivity)}, 'class_type':
            'AnyLineArtPreprocessor_aux'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def InpaintPreprocessor(self, image: IMAGE, mask: MASK,
        black_pixel_for_xinsir_cn: bool) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'mask': to_comfy_input(mask), 'black_pixel_for_xinsir_cn':
            to_comfy_input(black_pixel_for_xinsir_cn)}, 'class_type':
            'InpaintPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageLuminanceDetector(self, image: IMAGE, gamma_correction: float,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'gamma_correction': to_comfy_input(gamma_correction),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'ImageLuminanceDetector'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ImageIntensityDetector(self, image: IMAGE, gamma_correction: float,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'gamma_correction': to_comfy_input(gamma_correction),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'ImageIntensityDetector'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def LineartStandardPreprocessor(self, image: IMAGE, guassian_sigma:
        float, intensity_threshold: int, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'guassian_sigma': to_comfy_input(guassian_sigma),
            'intensity_threshold': to_comfy_input(intensity_threshold),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'LineartStandardPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def TEEDPreprocessor(self, image: IMAGE, safe_steps: int, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'safe_steps': to_comfy_input(safe_steps), 'resolution':
            to_comfy_input(resolution)}, 'class_type': 'TEEDPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def SavePoseKpsAsJsonFile(self, pose_kps: POSE_KEYPOINT,
        filename_prefix: str) ->None:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'pose_kps': to_comfy_input(pose_kps),
            'filename_prefix': to_comfy_input(filename_prefix)},
            'class_type': 'SavePoseKpsAsJsonFile'}
        self._add_node(node_id, comfy_json_node)

    def FacialPartColoringFromPoseKps(self, pose_kps: POSE_KEYPOINT, mode:
        str, skin: str, left_eye: str, right_eye: str, nose: str, upper_lip:
        str, inner_mouth: str, lower_lip: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'pose_kps': to_comfy_input(pose_kps),
            'mode': to_comfy_input(mode), 'skin': to_comfy_input(skin),
            'left_eye': to_comfy_input(left_eye), 'right_eye':
            to_comfy_input(right_eye), 'nose': to_comfy_input(nose),
            'upper_lip': to_comfy_input(upper_lip), 'inner_mouth':
            to_comfy_input(inner_mouth), 'lower_lip': to_comfy_input(
            lower_lip)}, 'class_type': 'FacialPartColoringFromPoseKps'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def UpperBodyTrackingFromPoseKps(self, pose_kps: POSE_KEYPOINT,
        id_include: str, Head_width_height: str, Neck_width_height: str,
        Shoulder_width_height: str, Torso_width_height: str,
        RArm_width_height: str, RForearm_width_height: str,
        LArm_width_height: str, LForearm_width_height: str) ->(TRACKING,
        StrNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'pose_kps': to_comfy_input(pose_kps),
            'id_include': to_comfy_input(id_include), 'Head_width_height':
            to_comfy_input(Head_width_height), 'Neck_width_height':
            to_comfy_input(Neck_width_height), 'Shoulder_width_height':
            to_comfy_input(Shoulder_width_height), 'Torso_width_height':
            to_comfy_input(Torso_width_height), 'RArm_width_height':
            to_comfy_input(RArm_width_height), 'RForearm_width_height':
            to_comfy_input(RForearm_width_height), 'LArm_width_height':
            to_comfy_input(LArm_width_height), 'LForearm_width_height':
            to_comfy_input(LForearm_width_height)}, 'class_type':
            'UpperBodyTrackingFromPoseKps'}
        self._add_node(node_id, comfy_json_node)
        return TRACKING(node_id, 0), StrNodeOutput(node_id, 1)

    def RenderPeopleKps(self, kps: POSE_KEYPOINT, render_body: bool,
        render_hand: bool, render_face: bool) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'kps': to_comfy_input(kps),
            'render_body': to_comfy_input(render_body), 'render_hand':
            to_comfy_input(render_hand), 'render_face': to_comfy_input(
            render_face)}, 'class_type': 'RenderPeopleKps'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def RenderAnimalKps(self, kps: POSE_KEYPOINT) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'kps': to_comfy_input(kps)},
            'class_type': 'RenderAnimalKps'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Zoe_DepthMapPreprocessor(self, image: IMAGE, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'Zoe-DepthMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DensePosePreprocessor(self, image: IMAGE, model: str, cmap: str,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'model': to_comfy_input(model), 'cmap': to_comfy_input(cmap),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'DensePosePreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Unimatch_OptFlowPreprocessor(self, image: IMAGE, ckpt_name: str,
        backward_flow: bool, bidirectional_flow: bool) ->(OPTICAL_FLOW, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'ckpt_name': to_comfy_input(ckpt_name), 'backward_flow':
            to_comfy_input(backward_flow), 'bidirectional_flow':
            to_comfy_input(bidirectional_flow)}, 'class_type':
            'Unimatch_OptFlowPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return OPTICAL_FLOW(node_id, 0), IMAGE(node_id, 1)

    def MaskOptFlow(self, optical_flow: OPTICAL_FLOW, mask: MASK) ->(
        OPTICAL_FLOW, IMAGE):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'optical_flow': to_comfy_input(
            optical_flow), 'mask': to_comfy_input(mask)}, 'class_type':
            'MaskOptFlow'}
        self._add_node(node_id, comfy_json_node)
        return OPTICAL_FLOW(node_id, 0), IMAGE(node_id, 1)

    def ScribblePreprocessor(self, image: IMAGE, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'ScribblePreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Scribble_XDoG_Preprocessor(self, image: IMAGE, threshold: int,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'threshold': to_comfy_input(threshold), 'resolution':
            to_comfy_input(resolution)}, 'class_type':
            'Scribble_XDoG_Preprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Scribble_PiDiNet_Preprocessor(self, image: IMAGE, safe: str,
        resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'safe': to_comfy_input(safe), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'Scribble_PiDiNet_Preprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DSINE_NormalMapPreprocessor(self, image: IMAGE, fov: float,
        iterations: int, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image), 'fov':
            to_comfy_input(fov), 'iterations': to_comfy_input(iterations),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'DSINE-NormalMapPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ShufflePreprocessor(self, image: IMAGE, resolution: int, seed: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution), 'seed':
            to_comfy_input(seed)}, 'class_type': 'ShufflePreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def MediaPipe_FaceMeshPreprocessor(self, image: IMAGE, max_faces: int,
        min_confidence: float, resolution: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'max_faces': to_comfy_input(max_faces), 'min_confidence':
            to_comfy_input(min_confidence), 'resolution': to_comfy_input(
            resolution)}, 'class_type': 'MediaPipe-FaceMeshPreprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def AIO_Preprocessor(self, image: IMAGE, preprocessor: str, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'preprocessor': to_comfy_input(preprocessor), 'resolution':
            to_comfy_input(resolution)}, 'class_type': 'AIO_Preprocessor'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ControlNetPreprocessorSelector(self, preprocessor: str
        ) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'preprocessor': to_comfy_input(
            preprocessor)}, 'class_type': 'ControlNetPreprocessorSelector'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def PixelPerfectResolution(self, original_image: IMAGE, image_gen_width:
        int, image_gen_height: int, resize_mode: str) ->IntNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'original_image': to_comfy_input(
            original_image), 'image_gen_width': to_comfy_input(
            image_gen_width), 'image_gen_height': to_comfy_input(
            image_gen_height), 'resize_mode': to_comfy_input(resize_mode)},
            'class_type': 'PixelPerfectResolution'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0)

    def ImageGenResolutionFromImage(self, image: IMAGE) ->(IntNodeOutput,
        IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'ImageGenResolutionFromImage'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0), IntNodeOutput(node_id, 1)

    def ImageGenResolutionFromLatent(self, latent: LATENT) ->(IntNodeOutput,
        IntNodeOutput):
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'latent': to_comfy_input(latent)},
            'class_type': 'ImageGenResolutionFromLatent'}
        self._add_node(node_id, comfy_json_node)
        return IntNodeOutput(node_id, 0), IntNodeOutput(node_id, 1)

    def HintImageEnchance(self, hint_image: IMAGE, image_gen_width: int,
        image_gen_height: int, resize_mode: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'hint_image': to_comfy_input(
            hint_image), 'image_gen_width': to_comfy_input(image_gen_width),
            'image_gen_height': to_comfy_input(image_gen_height),
            'resize_mode': to_comfy_input(resize_mode)}, 'class_type':
            'HintImageEnchance'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ExecuteAllControlNetPreprocessors(self, image: IMAGE, resolution: int
        ) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'resolution': to_comfy_input(resolution)}, 'class_type':
            'ExecuteAllControlNetPreprocessors'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def ControlNetAuxSimpleAddText(self, image: IMAGE, text: str) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'text': to_comfy_input(text)}, 'class_type':
            'ControlNetAuxSimpleAddText'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DepthAnything_V2(self, da_model: DAMODEL, images: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'da_model': to_comfy_input(da_model),
            'images': to_comfy_input(images)}, 'class_type': 'DepthAnything_V2'
            }
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def DownloadAndLoadDepthAnythingV2Model(self, model: str, precision: str
        ) ->DAMODEL:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'model': to_comfy_input(model),
            'precision': to_comfy_input(precision)}, 'class_type':
            'DownloadAndLoadDepthAnythingV2Model'}
        self._add_node(node_id, comfy_json_node)
        return DAMODEL(node_id, 0)

    def ShowText(self, text: str) ->StrNodeOutput:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'text': to_comfy_input(text)},
            'class_type': 'ShowText'}
        self._add_node(node_id, comfy_json_node)
        return StrNodeOutput(node_id, 0)

    def Pixelization(self, image: IMAGE, pixel_size: int, upscale_after:
        bool, copy_hue: bool, copy_sat: bool, copy_val: bool, restore_dark:
        int, restore_bright: int) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image),
            'pixel_size': to_comfy_input(pixel_size), 'upscale_after':
            to_comfy_input(upscale_after), 'copy_hue': to_comfy_input(
            copy_hue), 'copy_sat': to_comfy_input(copy_sat), 'copy_val':
            to_comfy_input(copy_val), 'restore_dark': to_comfy_input(
            restore_dark), 'restore_bright': to_comfy_input(restore_bright)
            }, 'class_type': 'Pixelization'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

    def Image_Remove_Background_rembg(self, image: IMAGE) ->IMAGE:
        node_id = random_node_id()
        comfy_json_node = {'inputs': {'image': to_comfy_input(image)},
            'class_type': 'Image Remove Background (rembg)'}
        self._add_node(node_id, comfy_json_node)
        return IMAGE(node_id, 0)

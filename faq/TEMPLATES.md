# Каталог шаблонов ComfyUI (Templates & Models)

Всего в базе `templates_models.db`: **116 шаблонов** и **343 модели**.

### Как использовать в RunPod:
- В CLI / Docker Command: `bash runpod-scripts/runpod_startup.sh --templates <ID>`
- Через переменные окружения: `COMFY_TEMPLATE_IDS=<ID1>,<ID2>`
- Пример для нескольких шаблонов: `--templates 89,93,94`

---

## 📁 Text to Image (18 шаблонов)

| ID | Название воркфлоу | Моделей | Требуемые модели и папки |
|:---:|:---|:---:|:---|
| **80** | Text to Image (Anima Base 1.0) | 3 | `diffusion_models/` **anima-base-v1.0.safetensors**<br>`text_encoders/` **qwen_3_06b_base.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **81** | Text to Image (Anima) | 3 | `diffusion_models/` **anima-base-v1.0.safetensors**<br>`text_encoders/` **qwen_3_06b_base.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **82** | Text to Image (Boogu Turbo) | 3 | `diffusion_models/` **boogu_image_turbo_fp8_scaled.safetensors**<br>`text_encoders/` **qwen3vl_8b_fp8_scaled.safetensors**<br>`vae/` **ae.safetensors** |
| **83** | Text to Image (Ernie Image Turbo) | 4 | `diffusion_models/` **ernie-image-turbo.safetensors**<br>`text_encoders/` **ernie-image-prompt-enhancer.safetensors**<br>`text_encoders/` **ministral-3-3b.safetensors**<br>`vae/` **flux2-vae.safetensors** |
| **84** | Text to Image (Ernie Image) | 4 | `diffusion_models/` **ernie-image.safetensors**<br>`text_encoders/` **ernie-image-prompt-enhancer.safetensors**<br>`text_encoders/` **ministral-3-3b.safetensors**<br>`vae/` **flux2-vae.safetensors** |
| **85** | Text to Image (Flux.1 Dev) | 4 | `diffusion_models/` **flux1-dev.safetensors**<br>`text_encoders/` **clip_l.safetensors**<br>`text_encoders/` **t5xxl_fp16.safetensors**<br>`vae/` **ae.safetensors** |
| **86** | Text to Image (Flux.1 Krea Dev) | 4 | `diffusion_models/` **flux1-krea-dev_fp8_scaled.safetensors**<br>`text_encoders/` **clip_l.safetensors**<br>`text_encoders/` **t5xxl_fp16.safetensors**<br>`vae/` **ae.safetensors** |
| **87** | Text to Image (Flux.2 Dev) | 4 | `diffusion_models/` **flux2_dev_fp8mixed.safetensors**<br>`loras/` **Flux_2-Turbo-LoRA_comfyui.safetensors**<br>`text_encoders/` **mistral_3_small_flux2_bf16.safetensors**<br>`vae/` **full_encoder_small_decoder.safetensors** |
| **88** | Text to Image (Ideogram v4) | 4 | `diffusion_models/` **ideogram4_fp8_scaled.safetensors**<br>`diffusion_models/` **ideogram4_unconditional_fp8_scaled.safetensors**<br>`text_encoders/` **qwen3vl_8b_fp8_scaled.safetensors**<br>`vae/` **flux2-vae.safetensors** |
| **89** | Text to Image (Krea-2 Turbo) | 4 | `diffusion_models/` **krea2_turbo_fp8_scaled.safetensors**<br>`loras/` **krea2_darkbrush.safetensors**<br>`text_encoders/` **qwen3vl_4b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **90** | Text to Image (Mage-Flow Turbo) | 3 | `diffusion_models/` **mage_flow_int8_convrot.safetensors**<br>`text_encoders/` **qwen3vl_4b_bf16.safetensors**<br>`vae/` **mage_flow_vae_bf16.safetensors** |
| **91** | Text to Image (Mage-Flow) | 3 | `diffusion_models/` **mage_flow_int8_convrot.safetensors**<br>`text_encoders/` **qwen3vl_4b_bf16.safetensors**<br>`vae/` **mage_flow_vae_bf16.safetensors** |
| **92** | Text to Image (NetaYume Lumina) | 1 | `checkpoints/` **NetaYumev35_pretrained_all_in_one.safetensors** |
| **93** | Text to Image (Qwen-Image 2512) | 4 | `diffusion_models/` **qwen_image_2512_fp8_e4m3fn.safetensors**<br>`loras/` **Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **94** | Text to Image (Qwen-Image) | 4 | `diffusion_models/` **qwen_image_fp8_e4m3fn.safetensors**<br>`loras/` **Qwen-Image-Lightning-8steps-V1.0.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **95** | Text to Image (Z-Image-Base) | 3 | `diffusion_models/` **z_image_bf16.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`vae/` **ae.safetensors** |
| **96** | Text to Image (Z-Image-Turbo) | 3 | `diffusion_models/` **z_image_turbo_bf16.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`vae/` **ae.safetensors** |
| **97** | Text to Image | 3 | `diffusion_models/` **z_image_turbo_bf16.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`vae/` **ae.safetensors** |

## 📁 Video (32 шаблонов)

| ID | Название воркфлоу | Моделей | Требуемые модели и папки |
|:---:|:---|:---:|:---|
| **5** | Canny to Video (LTX 2.0) | 6 | `checkpoints/` **ltx-2-19b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2-19b-dev-fp8.safetensors**<br>`latent_upscale_models/` **ltx-2-spatial-upscaler-x2-1.0.safetensors**<br>`loras/` **ltx-2-19b-distilled-lora-384.safetensors**<br>`loras/` **ltx-2-19b-ic-lora-canny-control.safetensors**<br>`text_encoders/` **gemma_3_12B_it_fp4_mixed.safetensors** |
| **18** | Depth to Video (ltx 2.0) | 9 | `checkpoints/` **ltx-2-19b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2-19b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2-19b-dev-fp8.safetensors**<br>`diffusion_models/` **lotus-depth-d-v1-1.safetensors**<br>`latent_upscale_models/` **ltx-2-spatial-upscaler-x2-1.0.safetensors**<br>`loras/` **ltx-2-19b-distilled-lora-384.safetensors**<br>`loras/` **ltx-2-19b-ic-lora-depth-control.safetensors**<br>`text_encoders/` **gemma_3_12B_it_fp4_mixed.safetensors**<br>`vae/` **vae-ft-mse-840000-ema-pruned.safetensors** |
| **21** | FLF2V (Wan2.1 VACE) | 4 | `diffusion_models/` **wan2.1_vace_14B_fp16.safetensors**<br>`loras/` **lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **wan_2.1_vae.safetensors** |
| **23** | First & Last Frame to Video (LTX-2.5) | 5 | `diffusion_models/` **ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors**<br>`text_encoders/` **gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors**<br>`text_encoders/` **gemma4_e2b_it_int8_convrot.safetensors**<br>`vae/` **ltx-2.5-audio-vae-bf16.safetensors**<br>`vae/` **ltx-2.5-video-vae-bf16.safetensors** |
| **24** | First-Last-Frame to Video (LTX-2.3) | 4 | `checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`text_encoders/` **gemma_3_12B_it_fp4_mixed.safetensors** |
| **25** | First-Last-Frame to Video | 4 | `checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`text_encoders/` **gemma_3_12B_it_fp4_mixed.safetensors** |
| **28** | Get Any Video Frame | 0 | *(стандартные узлы / без доп. моделей)* |
| **63** | Image to Video (LTX-2.3) | 6 | `checkpoints/` **ltx-2.3-22b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-dev-fp8.safetensors**<br>`latent_upscale_models/` **ltx-2.3-spatial-upscaler-x2-1.1.safetensors**<br>`loras/` **ltx-2.3-22b-distilled-lora-384.safetensors**<br>`text_encoders/` **gemma_3_12B_it_fp4_mixed.safetensors** |
| **64** | Image to Video (LTX-2.5) | 6 | `diffusion_models/` **ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors**<br>`latent_upscale_models/` **ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors**<br>`text_encoders/` **gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors**<br>`text_encoders/` **gemma4_e2b_it_int8_convrot.safetensors**<br>`vae/` **ltx-2.5-audio-vae-bf16.safetensors**<br>`vae/` **ltx-2.5-video-vae-bf16.safetensors** |
| **65** | Image to Video (MiniMax H3) | 5 | `diffusion_models/` **minimax_h3_fl2va_pruned_int8_convrot.safetensors**<br>`loras/` **minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors**<br>`text_encoders/` **qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors**<br>`vae/` **minimax_h3_audio_vae_fp32.safetensors**<br>`vae/` **minimax_h3_video_vae_fp16.safetensors** |
| **66** | Image to Video (Wan 2.2) | 6 | `diffusion_models/` **wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors**<br>`diffusion_models/` **wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors**<br>`loras/` **wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors**<br>`loras/` **wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **wan_2.1_vae.safetensors** |
| **67** | Image to Video (Wan Dancer) | 7 | `clip_vision/` **clip_vision_h.safetensors**<br>`diffusion_models/` **wan2.2_dancer_14b_global_fp8_scaled.safetensors**<br>`diffusion_models/` **wan2.2_dancer_14b_local_fp8_scaled.safetensors**<br>`loras/` **lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors**<br>`loras/` **lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors**<br>`text_encoders/` **umt5_xxl_fp16.safetensors**<br>`vae/` **Wan2_1_VAE_bf16.safetensors** |
| **68** | Merge Videos | 0 | *(стандартные узлы / без доп. моделей)* |
| **69** | Motion Transfer (Wan Animate 2 Distilled) | 4 | `clip_vision/` **clip_vision_h.safetensors**<br>`diffusion_models/` **wan_animate_2_distill_int8_convrot.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **Wan2_1_VAE_bf16.safetensors** |
| **70** | Motion Transfer (Wan Animate 2) | 5 | `clip_vision/` **clip_vision_h.safetensors**<br>`diffusion_models/` **wan_animate_2_int8_convrot.safetensors**<br>`loras/` **lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **Wan2_1_VAE_bf16.safetensors** |
| **73** | Pose to Video (LTX 2.0) | 7 | `checkpoints/` **ltx-2-19b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2-19b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2-19b-dev-fp8.safetensors**<br>`latent_upscale_models/` **ltx-2-spatial-upscaler-x2-1.0.safetensors**<br>`loras/` **ltx-2-19b-distilled-lora-384.safetensors**<br>`loras/` **ltx-2-19b-ic-lora-pose-control.safetensors**<br>`text_encoders/` **gemma_3_12B_it_fp4_mixed.safetensors** |
| **100** | Text to Video (LTX-2.3) | 6 | `checkpoints/` **ltx-2.3-22b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-dev-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-dev-fp8.safetensors**<br>`latent_upscale_models/` **ltx-2.3-spatial-upscaler-x2-1.1.safetensors**<br>`loras/` **ltx-2.3-22b-distilled-lora-384.safetensors**<br>`text_encoders/` **gemma_3_12B_it_fp4_mixed.safetensors** |
| **101** | Text to Video (LTX-2.5) | 6 | `diffusion_models/` **ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors**<br>`latent_upscale_models/` **ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors**<br>`text_encoders/` **gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors**<br>`text_encoders/` **gemma4_e2b_it_int8_convrot.safetensors**<br>`vae/` **ltx-2.5-audio-vae-bf16.safetensors**<br>`vae/` **ltx-2.5-video-vae-bf16.safetensors** |
| **102** | Text to Video (Wan 2.2) | 6 | `diffusion_models/` **wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors**<br>`diffusion_models/` **wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors**<br>`loras/` **wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors**<br>`loras/` **wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **wan_2.1_vae.safetensors** |
| **104** | Upscale Video (SeedVR2 3B Int8) | 2 | `diffusion_models/` **seedvr2_3b_int8_convrot.safetensors**<br>`vae/` **seedvr2_ema_vae_fp16.safetensors** |
| **105** | Video Captioning (Gemini) | 0 | *(стандартные узлы / без доп. моделей)* |
| **106** | Video Depth Estimation (Depth Anything 3) | 1 | `geometry_estimation/` **depth_anything_3_mono_large.safetensors** |
| **107** | Video Depth Estimation (MoGe) | 1 | `geometry_estimation/` **moge_2_vitl_normal_fp16.safetensors** |
| **108** | Video Edit (Bernini-R) | 6 | `diffusion_models/` **wan2.2_bernini_r_high_noise_fp8_scaled.safetensors**<br>`diffusion_models/` **wan2.2_bernini_r_low_noise_fp8_scaled.safetensors**<br>`loras/` **lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors**<br>`loras/` **lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **Wan2_1_VAE_bf16.safetensors** |
| **109** | Video Face Detection (Mediapipe) | 1 | `detection/` **mediapipe_face_fp32.safetensors** |
| **110** | Video Generation (LTX-2.3 IC-LoRA) | 6 | `checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`checkpoints/` **ltx-2.3-22b-distilled-fp8.safetensors**<br>`loras/` **gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors**<br>`loras/` **ltx-2.3-22b-ic-lora-ingredients-0.9.safetensors**<br>`text_encoders/` **gemma_3_12B_it_fp4_mixed.safetensors** |
| **111** | Video Inpaint (VOID) | 6 | `checkpoints/` **sam3.1_multiplex_fp16.safetensors**<br>`diffusion_models/` **void_pass1.safetensors**<br>`diffusion_models/` **void_pass2.safetensors**<br>`optical_flow/` **raft_large_C_T_SKHT_V2-ff5fadd5.safetensors**<br>`text_encoders/` **t5xxl_fp16.safetensors**<br>`vae/` **cogvideox_vae.safetensors** |
| **112** | Video Inpainting (Wan2.1 VACE) | 5 | `checkpoints/` **sam3.1_multiplex_fp16.safetensors**<br>`diffusion_models/` **wan2.1_vace_14B_fp16.safetensors**<br>`loras/` **Wan21_CausVid_14B_T2V_lora_rank32.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **wan_2.1_vae.safetensors** |
| **113** | Video Segmentation (SAM3) | 1 | `checkpoints/` **sam3.1_multiplex_fp16.safetensors** |
| **114** | Video Stitch | 0 | *(стандартные узлы / без доп. моделей)* |
| **115** | Video Upscale(GAN x4) | 1 | `upscale_models/` **RealESRGAN_x4plus.safetensors** |
| **116** | Video to Pose Map (SDPose Multi-Person) | 2 | `checkpoints/` **sdpose_wholebody_fp16.safetensors**<br>`diffusion_models/` **rt_detr_v4-x-hgnet_fp16.safetensors** |

## 📁 Image Edit & Inpaint (14 шаблонов)

| ID | Название воркфлоу | Моделей | Требуемые модели и папки |
|:---:|:---|:---:|:---|
| **20** | Edit Image (Boogu Image Edit) | 3 | `diffusion_models/` **boogu_image_edit_fp8_scaled.safetensors**<br>`text_encoders/` **qwen3vl_8b_fp8_scaled.safetensors**<br>`vae/` **ae.safetensors** |
| **39** | Image Edit (Bernini-R) | 6 | `diffusion_models/` **wan2.2_bernini_r_high_noise_fp8_scaled.safetensors**<br>`diffusion_models/` **wan2.2_bernini_r_low_noise_fp8_scaled.safetensors**<br>`loras/` **lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors**<br>`loras/` **lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **Wan2_1_VAE_bf16.safetensors** |
| **40** | Image Edit (FireRed Image Edit 1.1) | 4 | `diffusion_models/` **FireRed-Image-Edit-1.1-transformer.safetensors**<br>`loras/` **FireRed-Image-Edit-1.0-Lightning-8steps-v1.0.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **41** | Image Edit (Flux.2 Dev) | 4 | `diffusion_models/` **flux2_dev_fp8mixed.safetensors**<br>`loras/` **Flux_2-Turbo-LoRA_comfyui.safetensors**<br>`text_encoders/` **mistral_3_small_flux2_bf16.safetensors**<br>`vae/` **full_encoder_small_decoder.safetensors** |
| **42** | Image Edit (Flux.2 Klein 4B) | 3 | `diffusion_models/` **flux-2-klein-base-4b-fp8.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`vae/` **flux2-vae.safetensors** |
| **43** | Image Edit (Joy Image Edit) | 3 | `diffusion_models/` **joyai_image_edit_int8_convrot.safetensors**<br>`text_encoders/` **qwen3vl_8b_joyimage_edit_int8_convrot.safetensors**<br>`vae/` **wan_2.1_vae.safetensors** |
| **44** | Image Edit (LongCat Image Edit) | 3 | `diffusion_models/` **longcat_image_edit_bf16.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **ae.safetensors** |
| **45** | Image Edit (Mage-Flow-Edit Turbo) | 3 | `diffusion_models/` **mage_flow_edit_turbo_int8_convrot.safetensors**<br>`text_encoders/` **qwen3vl_4b_bf16.safetensors**<br>`vae/` **mage_flow_vae_bf16.safetensors** |
| **46** | Image Edit (Mage-Flow-Edit) | 3 | `diffusion_models/` **mage_flow_edit_int8_convrot.safetensors**<br>`text_encoders/` **qwen3vl_4b_bf16.safetensors**<br>`vae/` **mage_flow_vae_bf16.safetensors** |
| **47** | Image Edit (Qwen 2509) | 4 | `diffusion_models/` **qwen_image_edit_2509_fp8_e4m3fn.safetensors**<br>`loras/` **Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **48** | Image Edit (Qwen 2511) | 3 | `diffusion_models/` **qwen_image_edit_2511_bf16.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **50** | Image Inpainting (Flux.1 Fill Dev) | 4 | `diffusion_models/` **flux1-fill-dev.safetensors**<br>`text_encoders/` **clip_l.safetensors**<br>`text_encoders/` **t5xxl_fp16.safetensors**<br>`vae/` **ae.safetensors** |
| **51** | Image Inpainting (Qwen-image) | 5 | `controlnet/` **Qwen-Image-InstantX-ControlNet-Inpainting.safetensors**<br>`diffusion_models/` **qwen_image_fp8_e4m3fn.safetensors**<br>`loras/` **Qwen-Image-Lightning-4steps-V1.0.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **54** | Image Outpainting (Qwen-Image) | 5 | `controlnet/` **Qwen-Image-InstantX-ControlNet-Inpainting.safetensors**<br>`diffusion_models/` **qwen_image_fp8_e4m3fn.safetensors**<br>`loras/` **Qwen-Image-Lightning-4steps-V1.0.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |

## 📁 Audio & Music (6 шаблонов)

| ID | Название воркфлоу | Моделей | Требуемые модели и папки |
|:---:|:---|:---:|:---|
| **1** | Audio Generation (Stable Audio 3 Medium Base) | 3 | `checkpoints/` **stable_audio_3_medium_base.safetensors**<br>`text_encoders/` **qwen3.5_2b_bf16.safetensors**<br>`text_encoders/` **t5gemma_b_b_ul2.safetensors** |
| **2** | Audio Generation (Stable Audio 3 Medium) | 3 | `checkpoints/` **stable_audio_3_medium.safetensors**<br>`text_encoders/` **qwen3.5_2b_bf16.safetensors**<br>`text_encoders/` **t5gemma_b_b_ul2.safetensors** |
| **71** | Music Cover (YuE2) | 2 | `audio_encoders/` **sheetsage2_bf16.safetensors**<br>`checkpoints/` **yue2_3b_int8_convrot.safetensors** |
| **79** | Text to Audio (ACE-Step 1.5) | 4 | `diffusion_models/` **acestep_v1.5_turbo.safetensors**<br>`text_encoders/` **qwen_0.6b_ace15.safetensors**<br>`text_encoders/` **qwen_4b_ace15.safetensors**<br>`vae/` **ace_1.5_vae.safetensors** |
| **98** | Text to Music (MiniMax Music 3) | 3 | `diffusion_models/` **minimax_music3_dit_fp16.safetensors**<br>`text_encoders/` **minimax_music3_text_encoder_pruned_int8_convrot.safetensors**<br>`vae/` **minimax_music3_dav.safetensors** |
| **99** | Text to Music (YuE2) | 1 | `checkpoints/` **yue2_3b_int8_convrot.safetensors** |

## 📁 Vision & Estimation (13 шаблонов)

| ID | Название воркфлоу | Моделей | Требуемые модели и папки |
|:---:|:---|:---:|:---|
| **17** | Depth to Image (Z-Image-Turbo) | 6 | `diffusion_models/` **lotus-depth-d-v1-1.safetensors**<br>`diffusion_models/` **z_image_turbo_bf16.safetensors**<br>`model_patches/` **Z-Image-Turbo-Fun-Controlnet-Union.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`vae/` **ae.safetensors**<br>`vae/` **vae-ft-mse-840000-ema-pruned.safetensors** |
| **27** | Geometry Estimation (MoGe) | 1 | `geometry_estimation/` **moge_2_vitl_normal_fp16.safetensors** |
| **31** | Image Albedo Estimation (Marigold V2) | 4 | `diffusion_models/` **qwen_image_edit_2509_int8_convrot.safetensors**<br>`embeddings/` **marigold_v2_albedo_conditioning.safetensors**<br>`loras/` **marigold_v2_albedo.safetensors**<br>`vae/` **marigold_v2_albedo_vae.safetensors** |
| **35** | Image Depth Estimation (Depth Anything 3) | 1 | `geometry_estimation/` **depth_anything_3_mono_large.safetensors** |
| **36** | Image Depth Estimation (Lotus Depth) | 2 | `diffusion_models/` **lotus-depth-d-v1-1.safetensors**<br>`vae/` **vae-ft-mse-840000-ema-pruned.safetensors** |
| **37** | Image Depth Estimation (Marigold V2) | 4 | `diffusion_models/` **qwen_image_edit_2509_int8_convrot.safetensors**<br>`embeddings/` **marigold_v2_depth_conditioning.safetensors**<br>`loras/` **marigold_v2_depth_log_stage2.safetensors**<br>`vae/` **marigold_v2_depth_log_stage2_vae.safetensors** |
| **38** | Image Depth Estimation (MoGe) | 1 | `geometry_estimation/` **moge_2_vitl_normal_fp16.safetensors** |
| **49** | Image Face Detection (Mediapipe) | 1 | `detection/` **mediapipe_face_fp32.safetensors** |
| **53** | Image Normal Estimation (Marigold V2) | 4 | `diffusion_models/` **qwen_image_edit_2509_int8_convrot.safetensors**<br>`embeddings/` **marigold_v2_normals_conditioning.safetensors**<br>`loras/` **marigold_v2_normals.safetensors**<br>`vae/` **marigold_v2_normals_vae.safetensors** |
| **55** | Image Segmentation (SAM3) | 1 | `checkpoints/` **sam3.1_multiplex_fp16.safetensors** |
| **61** | Image to Pose Map (SDPose Multi-Person) | 2 | `checkpoints/` **sdpose_wholebody_fp16.safetensors**<br>`diffusion_models/` **rt_detr_v4-x-hgnet_fp16.safetensors** |
| **62** | Image to Pose Map (SDPose-OOD) | 1 | `checkpoints/` **sdpose_wholebody_fp16.safetensors** |
| **72** | Pose to Image (Z-Image-Turbo) | 4 | `diffusion_models/` **z_image_turbo_bf16.safetensors**<br>`model_patches/` **Z-Image-Turbo-Fun-Controlnet-Union.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`vae/` **ae.safetensors** |

## 📁 ControlNet & Canny (3 шаблонов)

| ID | Название воркфлоу | Моделей | Требуемые модели и папки |
|:---:|:---|:---:|:---|
| **4** | Canny to Image (Z-Image-Turbo) | 4 | `diffusion_models/` **z_image_turbo_bf16.safetensors**<br>`model_patches/` **Z-Image-Turbo-Fun-Controlnet-Union.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`vae/` **ae.safetensors** |
| **13** | Control to Image (Anima LLLite) | 5 | `diffusion_models/` **anima-base-v1.0.safetensors**<br>`loras/` **anima-turbo-lora-v0.2.safetensors**<br>`model_patches/` **anima-lllite-inpainting-v2.safetensors**<br>`text_encoders/` **qwen_3_06b_base.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **14** | ControlNet (Z-Image-Turbo) | 4 | `diffusion_models/` **z_image_turbo_bf16.safetensors**<br>`model_patches/` **Z-Image-Turbo-Fun-Controlnet-Union.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`vae/` **ae.safetensors** |

## 📁 Upscale (1 шаблонов)

| ID | Название воркфлоу | Моделей | Требуемые модели и папки |
|:---:|:---|:---:|:---|
| **57** | Image Upscale(Z-image-Turbo) | 4 | `diffusion_models/` **z_image_turbo_bf16.safetensors**<br>`text_encoders/` **qwen_3_4b.safetensors**<br>`upscale_models/` **RealESRGAN_x4plus.safetensors**<br>`vae/` **ae.safetensors** |

## 📁 Other (29 шаблонов)

| ID | Название воркфлоу | Моделей | Требуемые модели и папки |
|:---:|:---|:---:|:---|
| **3** | Brightness and Contrast | 0 | *(стандартные узлы / без доп. моделей)* |
| **6** | Character Replacement (SCAIL-2 Base) | 7 | `checkpoints/` **sam3.1_multiplex_fp16.safetensors**<br>`clip_vision/` **clip_vision_h.safetensors**<br>`diffusion_models/` **wan2.1_14B_SCAIL_2_fp16.safetensors**<br>`loras/` **lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors**<br>`loras/` **wan2.1_SCAIL_2_DPO_lora_bf16.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **Wan2_1_VAE_bf16.safetensors** |
| **7** | Character Replacement (SCAIL-2 Extend) | 7 | `checkpoints/` **sam3.1_multiplex_fp16.safetensors**<br>`clip_vision/` **clip_vision_h.safetensors**<br>`diffusion_models/` **wan2.1_14B_SCAIL_2_fp16.safetensors**<br>`loras/` **lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors**<br>`loras/` **wan2.1_SCAIL_2_DPO_lora_bf16.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **Wan2_1_VAE_bf16.safetensors** |
| **8** | Character Replacement (SCAIL-2 Int8 Base) | 7 | `checkpoints/` **sam3.1_multiplex_fp16.safetensors**<br>`clip_vision/` **clip_vision_h.safetensors**<br>`diffusion_models/` **wan2.1_14B_SCAIL_2_int8_convrot.safetensors**<br>`loras/` **lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors**<br>`loras/` **wan2.1_SCAIL_2_DPO_lora_bf16.safetensors**<br>`text_encoders/` **umt5_xxl_fp8_e4m3fn_scaled.safetensors**<br>`vae/` **Wan2_1_VAE_bf16.safetensors** |
| **9** | Chromatic Aberration | 0 | *(стандартные узлы / без доп. моделей)* |
| **10** | Color Adjustment | 0 | *(стандартные узлы / без доп. моделей)* |
| **11** | Color Balance | 0 | *(стандартные узлы / без доп. моделей)* |
| **12** | Color Curves | 0 | *(стандартные узлы / без доп. моделей)* |
| **15** | Crop Images 2x2 | 0 | *(стандартные узлы / без доп. моделей)* |
| **16** | Crop Images 3x3 | 0 | *(стандартные узлы / без доп. моделей)* |
| **19** | Edge-Preserving Blur | 0 | *(стандартные узлы / без доп. моделей)* |
| **22** | Film Grain | 0 | *(стандартные узлы / без доп. моделей)* |
| **26** | Frame Interpolation | 1 | `frame_interpolation/` **film_net_fp16.safetensors** |
| **29** | Glow | 0 | *(стандартные узлы / без доп. моделей)* |
| **30** | Hue and Saturation | 0 | *(стандартные узлы / без доп. моделей)* |
| **32** | Image Blur | 0 | *(стандартные узлы / без доп. моделей)* |
| **33** | Image Captioning (gemini) | 0 | *(стандартные узлы / без доп. моделей)* |
| **34** | Image Channels | 0 | *(стандартные узлы / без доп. моделей)* |
| **52** | Image Levels | 0 | *(стандартные узлы / без доп. моделей)* |
| **56** | Image Style Reference (Krea-2 Turbo) | 4 | `diffusion_models/` **krea2_turbo_int8_convrot.safetensors**<br>`loras/` **krea2_style_reference.safetensors**<br>`text_encoders/` **qwen3vl_4b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_vae.safetensors** |
| **58** | Image to Gaussian Splat (TripoSplat) | 5 | `background_removal/` **birefnet.safetensors**<br>`clip_vision/` **dino_v3_vit_h.safetensors**<br>`diffusion_models/` **triposplat_fp16.safetensors**<br>`vae/` **flux2-vae.safetensors**<br>`vae/` **triposplat_vae_decoder_fp16.safetensors** |
| **59** | Image to Layers(Qwen-Image-Layered) | 3 | `diffusion_models/` **qwen_image_layered_bf16.safetensors**<br>`text_encoders/` **qwen_2.5_vl_7b_fp8_scaled.safetensors**<br>`vae/` **qwen_image_layered_vae.safetensors** |
| **60** | Image to Model (Hunyuan3d 2.1) | 1 | `checkpoints/` **hunyuan_3d_v2.1.safetensors** |
| **74** | Prompt Enhance | 0 | *(стандартные узлы / без доп. моделей)* |
| **75** | Remove Background (BiRefNet) | 1 | `background_removal/` **birefnet.safetensors** |
| **76** | Select Per-Line Text by Index | 0 | *(стандартные узлы / без доп. моделей)* |
| **77** | Sharpen | 0 | *(стандартные узлы / без доп. моделей)* |
| **78** | Split Image Grid to Tiles | 0 | *(стандартные узлы / без доп. моделей)* |
| **103** | Unsharp Mask | 0 | *(стандартные узлы / без доп. моделей)* |

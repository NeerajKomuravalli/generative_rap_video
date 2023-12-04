# """
from llm.gpt import get_gpt_3_5_resp
from segmind.controlnet_canny import controlnet_canny
from segmind.stable_diffusion import stable_diffusion
from segmind.paragon import paragon
from segmind.settings import STABLE_DIFFUSION_STYLES as style
from segmind.prompts import STYLE_PICK
from stable_diffussion.stable_diffussion import text_to_image

if __name__ == "__main__":
    prompt = "A disco party with people having fun dancing."
    save_image_path = "./paragon.jpg"
    image_path = "/Users/neeraj/Downloads/test-image.jpg"
    # controlnet_canny(
    #     prompt,
    #     image_path,
    #     save_image_path,
    # )
    text_to_image()
# """

"""
image_folder_path = "results/results_3_5_turbo_16k/"
audio_file_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111.wav"
srt_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation.srt"
save_video_path = (
    "results/video/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_stable_diff.mp4"
)
save_video_path_with_audio = "results/video/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_stable_diff_with_context_audio.mp4"
create_video(
    image_folder_path,
    audio_file_path,
    save_video_path,
    save_video_path_with_audio,
)
"""
"""
srt_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation.srt"
context_srt_file_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation_context.srt"
save_images_folder_path = "/Users/neeraj/Work/generative_rap_video/src/results/results_3_5_turbo_16k_w_o_context_base_model/"
generate_images_from_srt(
    srt_path,
    # context_srt_file_path,
    save_images_folder_path,
)
"""
"""
ffmpeg -i results/video/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_stable_diff.mp4 -i ../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111.wav -c:v copy -c:a aac -strict experimental results/video/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_stable_diff_ffmpeg.mp4
"""

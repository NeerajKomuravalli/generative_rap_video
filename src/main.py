# """
from segmind.controlnet_canny import controlnet_canny
from segmind.stable_diffusion import stable_diffusion
from segmind.paragon import paragon
from segmind.settings import STABLE_DIFFUSION_STYLES as style
from segmind.prompts import STYLE_PICK

# from stable_diffussion.stable_diffussion import text_to_image
from video_gen.srt_to_images_with_summary import generate_images
from video_gen.create_video_from_frames import create_video

if __name__ == "__main__":
    """
    from llm.gpt import GPT3Chat

    gpt = GPT3Chat("gpt-4")
    resp = gpt.get_response(
        '''I want to use stable diffusion 1.5 to generate images for a rap video. As a rap video has a theme I would like GPT to generate prompt that will make stable diffusion generate images that has similar style.
        Modify the above prompt that can be used by gpt to generate coherent images
        '''
    )
    # Generate a prompt to create coherent and stylistically similar images using stable diffusion 1.5 for a thematic rap video.
    print(resp)
    """
    """
    prompt = "A disco party with people having fun dancing."
    save_image_path = "./paragon.jpg"
    image_path = "/Users/neeraj/Downloads/test-image.jpg"
    # controlnet_canny(
    #     prompt,
    #     image_path,
    #     save_image_path,
    # )
    # text_to_image()
    """
    """
    srt_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation.srt"
    save_images_folder_path = "/Users/neeraj/Work/generative_rap_video/src/results/results_3_5_turbo_16k_summary/"
    models = ["anime", "base", "graffiti", "pop art", "renaissance"]
    generate_images(srt_path, save_images_folder_path, models)
    """
    # """

    # """
    import os

    folder_path = "results/results_3_5_turbo_16k_summary/"
    audio_file_path = (
        "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_08_12_23.wav"
    )
    srt_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation.srt"
    save_video_folder_path = "results/video/10_12_23/"
    video_file_prefix = (
        "karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_w_summary_stable_diff_%s.mp4"
    )
    for folder_name in os.listdir(folder_path):
        if folder_name == ".DS_Store":
            continue
        image_folder_path = os.path.join(folder_path, folder_name)
        save_video_path = os.path.join(
            save_video_folder_path, video_file_prefix % (folder_name)
        )
        create_video(
            image_folder_path,
            audio_file_path,
            save_video_path,
        )
    """
    image_folder_path = "results/results_3_5_turbo_16k_summary/pop art/"
    audio_file_path = (
        "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111.wav"
    )
    srt_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation.srt"
    save_video_path = "results/video/10_12_23/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_w_summary_stable_diff_pop+art.mp4"
    save_video_path_with_audio = "results/video/10_12_23/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_w_summary_stable_diff_pop_art_audio.mp4"
    create_video(
        image_folder_path,
        audio_file_path,
        save_video_path,
        save_video_path_with_audio,
    )
    """
# """
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

"""
Summary : The rap track is about the rapper's dilemma in making decisions and facing societal pressures. They are being questioned by a friend about what they want to do, whether it's going to the club, eating and enjoying, or smoking and chilling in pajamas. The rapper feels confused and unable to make choices due to the limitations of their brain and external influences. They feel like a joker and perceive the world around them as uncertain, comparing their decisions to the tensions between Ukraine and Russia. The rapper wants to avoid conflict and instead experiences panic attacks, taking a diplomatic approach. They express frustration with their nagging friends and respond with defiance by writing this rap as a way to release their emotions. The rapper emphasizes their search for direction, comparing themselves to Monkey D. Luffy and their journey to find their own map.
"""

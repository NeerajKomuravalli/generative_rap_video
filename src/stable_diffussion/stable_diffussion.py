import requests
import json


def image_to_image():
    pass


def text_to_image():
    url = "https://stablediffusionapi.com/api/v3/text2img"

    payload = json.dumps(
        {
            "key": "erNsUfC8qxzG3rxbcwoAzxTzgNcF7oOm0dyivdReUliFdysuaMMN7jVkUDIJ",
            # "prompt": "ultra realistic close up portrait ((beautiful pale cyberpunk female with heavy black eyeliner))",
            # "prompt": "ultra realistic scene with an active night life with three people in close up smoking, eating and dancing",
            # "prompt": "Realistic scene of two people smoking and drinking where the centre of the faces are at (50, 50) and (100, 150) coordinates",
            "prompt": "People dancing in the club and having a good time with focus on at least one person but we should be able to see them dance, 4k",
            "negative_prompt": None,
            "width": "512",
            "height": "512",
            "samples": "1",
            "num_inference_steps": "20",
            "seed": None,
            "guidance_scale": 7.5,
            "safety_checker": "yes",
            "multi_lingual": "no",
            "panorama": "no",
            "self_attention": "no",
            "upscale": "no",
            "embeddings_model": None,
            "webhook": None,
            "track_id": None,
        }
    )

    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return response.text


def image_to_image():
    url = "https://stablediffusionapi.com/api/v3/img2img"

    payload = json.dumps(
        {
            "key": "erNsUfC8qxzG3rxbcwoAzxTzgNcF7oOm0dyivdReUliFdysuaMMN7jVkUDIJ",
            "prompt": "Generate an image that looks exactly like the reference image but they turned their heads a little bit",
            "negative_prompt": None,
            # "init_image": "https://cdn2.stablediffusionapi.com/generations/3315f4d3-1dc8-43a3-8690-80b05f336175-0.png",
            "init_image": "https://pub-3626123a908346a7a8be8d9295f44e26.r2.dev/generations/0ad14ea5-3177-49da-ac64-b57c9afd1dda-0.png",
            "width": "512",
            "height": "512",
            "samples": "1",
            "num_inference_steps": "30",
            "safety_checker": "no",
            "enhance_prompt": "yes",
            "guidance_scale": 7.5,
            "strength": 0.7,
            "seed": None,
            "webhook": None,
            "track_id": None,
        }
    )

    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return response.text


text_to_image()

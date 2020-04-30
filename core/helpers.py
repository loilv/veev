from datetime import datetime
import requests
import os
import json
import random
base_dir = os.path.dirname(os.path.realpath(__file__))


def handle_make_audio(text, voice, speed, output_type):
    try:
        key = [
            'SNxGGJ1CHZjBr3op9TL5X4ldZhc7RDVAcQ6PnvVHjj0GLZYnrgmagaOErArToIMM',
            'w1SqUDVyFPYXHhpUV8HiRfUQiUCuBK-ttAJe4N2T0gpOTBMZybhhWqDcm18jKJwS',
            'iPMb3fudkMakf7hqXYORU6-40KASGstUNVXPtfEFXZq-MbIBbP4YwuEpyHVRONaW'
        ]

        url = 'https://viettelgroup.ai/voice/api/tts/v1/rest/syn'
        headers = {
            'Content-Type': 'application/json',
            'token': random.choice(key)
        }

        data = dict(
            text=text,
            voice=voice,
            id='voice-{}'.format(datetime.now()),
            speed=float(speed),
            tts_return_option=output_type
        )

        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(response.headers)
        print(response.status_code)

        if int(output_type) == 2:
            o_t = '.mp3'
        else:
            o_t = '.wav'

        data = response.content
        name_of_file = '{}-{}'.format(voice, datetime.now().strftime('%d-%m-%Y'))
        save_path = os.path.dirname(os.path.realpath(__file__)) + '/media/audio/'
        completeName = os.path.join(save_path, name_of_file + o_t)
        f = open(completeName, 'wb+')
        f.write(data)
        f.close()

        return completeName
    except Exception as e:
        print(e)
        return False


def handle_upload_file(file, name, path):
    name_of_file = '{}'.format(name)
    save_path = base_dir + '/media/' + path + '/'
    completeName = os.path.join(save_path, name_of_file)
    with open(completeName, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return completeName


def get_image_from_url(url, name, path, chunk=2048):
    name_of_file = '{}.jpg'.format(name)
    save_path = base_dir + '/media/' + path + '/'
    completeName = os.path.join(save_path, name_of_file)
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(completeName, 'wb+') as f:
            for chunk in res.iter_content(chunk):
                f.write(chunk)
            f.close()
    return completeName
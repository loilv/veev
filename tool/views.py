# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from django.http import HttpResponse
from django.shortcuts import render
from core import scripts, helpers
from wsgiref.util import FileWrapper
# Create your views here.


def index(request):
    return render(request, 'tool.html')


def create_video(request):
    intro, outro = None, None
    if request.method == 'POST':
        param = request.POST
        files = request.FILES
        audio = helpers.handle_make_audio(param['t-content'], param['s-voice'], 0.8, 2)
        sub = scripts.generate_sub(audio)

        if 'f-intro' in files:
            intro = helpers.handle_upload_file(files['f-intro'], files['f-intro'].name, 'intro')
        if 'f-outro' in files:
            outro = helpers.handle_upload_file(files['f-outro'], files['f-outro'].name, 'outro')

        bg_music = helpers.handle_upload_file(files['f-bg-music'], files['f-bg-music'].name, 'bg-music')
        audio_bg = scripts.handle_create_bg_music(files['f-bg-music'], audio, param['i-volume'])
        images = request.POST['i-images']
        list_images = images.split(',')
        i = 0
        for img in list_images:
            i += 1
            try:
                helpers.get_image_from_url(img, 'images-{}'.format(i), 'images')
            except Exception as e:
                print(e)
                continue
        video = scripts.transition_fade_in()
        video_prod = scripts.handle_create_video_loop(video=video, audio=audio_bg)
        file_complete = scripts.merge_video_sub(video_prod, sub, 'complete')
        if intro and outro:
            file_complete = scripts.handle_merge_into_outro(
                intro=intro, video=file_complete, outro=outro, name='full'
            )
        file = FileWrapper(open(file_complete, 'rb'))
        response = HttpResponse(file, content_type="video/mp4")

        response['Content-Disposition'] = 'attachment; filename={name}'.format(name=param['i-name'] + '.mp4')
        return response


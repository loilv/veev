import os
import subprocess
from datetime import datetime
from . import helpers

base_dir = os.path.dirname(os.path.realpath(__file__))


def transition_fade_in():
    source_path = base_dir + '/media/images/'
    save_path = base_dir + '/media/video/'
    list_file = os.listdir(source_path)
    number_files = len(list_file)
    WIDTH = 1280
    HEIGHT = 720
    FPS = 30
    TRANSITION_DURATION = 1
    IMAGE_DURATION = 10
    SCREEN_MODE = 4  # 1=CENTER, 2=CROP, 3=SCALE, 4=BLUR
    BACKGROUND_COLOR = "black"

    # INTERNAL VARIABLES
    TRANSITION_FRAME_COUNT = TRANSITION_DURATION * FPS
    IMAGE_FRAME_COUNT = IMAGE_DURATION * FPS
    TOTAL_DURATION = IMAGE_DURATION + TRANSITION_DURATION * number_files - TRANSITION_DURATION
    TOTAL_FRAME_COUNT = TOTAL_DURATION * FPS

    # 1. START COMMAND
    FULL_SCRIPT = "ffmpeg -y "
    for i in list_file:
        FULL_SCRIPT += ' -loop 1 -i {} '.format(source_path + i)

    # 3. START FILTER COMPLEX
    FULL_SCRIPT += "-filter_complex \""

    # 4. PREPARE INPUTS
    for i in range(number_files):
        if SCREEN_MODE == 1:
            FULL_SCRIPT += "[{i}:v]setpts=PTS-STARTPTS," \
                           "scale=w='if(gte(iw/ih,{width}/{height})," \
                           "min(iw,{width}),-1)':h='if(gte(iw/ih,{width}/{height}),-1," \
                           "min(ih,{height}))'," \
                           "scale=trunc(iw/2)*2:trunc(ih/2)*2," \
                           "setsar=sar=1/1," \
                           "fps={fps}," \
                           "format=rgba," \
                           "split=2[stream{i1}out1][stream{i1}out2];". \
                format(i=i, i1=i + 1, width=WIDTH, height=HEIGHT, fps=FPS)
        elif SCREEN_MODE == 2:
            FULL_SCRIPT += "[{i}:v]setpts=PTS-STARTPTS," \
                           "scale=w='if(gte(iw/ih,{width}/{height}),-1,{width})':h='if(gte(iw/ih,{width}/{height}),{height},-1)'," \
                           "crop={width}:{height}," \
                           "setsar=sar=1/1,fps={fps}," \
                           "format=rgba,split=2[stream{i1}out1][stream{i1}out2];" \
                .format(i=i, i1=i + 1, width=WIDTH, height=HEIGHT, fps=FPS)
        elif SCREEN_MODE == 3:
            FULL_SCRIPT += "[{i}:v]setpts=PTS-STARTPTS," \
                           "scale={width}:{height},setsar=sar=1/1," \
                           "fps={fps},format=rgba," \
                           "split=2[stream{i1}out1][stream{i1}out2];" \
                .format(i=i, i1=i + 1, width=WIDTH, height=HEIGHT, fps=FPS)
        elif SCREEN_MODE == 4:
            FULL_SCRIPT += "[{i}:v]scale={width}x{height}," \
                           "setsar=sar=1/1," \
                           "fps={fps}," \
                           "format=rgba," \
                           "boxblur=100," \
                           "setsar=sar=1/1[stream{i}blurred];".format(i=i, i1=i + 1, width=WIDTH, height=HEIGHT,
                                                                      fps=FPS)
            FULL_SCRIPT += "[{i}:v]scale=w='if(gte(iw/ih,{width}/{height})," \
                           "min(iw,{width}),-1)':h='if(gte(iw/ih,{width}/{height}),-1," \
                           "min(ih,{height}))',scale=trunc(iw/2)*2:trunc(ih/2)*2," \
                           "setsar=sar=1/1," \
                           "fps={fps}," \
                           "format=rgba[stream{i}raw];".format(i=i, i1=i + 1, width=WIDTH, height=HEIGHT, fps=FPS)
            FULL_SCRIPT += "[stream{i}blurred][stream{i}raw]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:format=rgb," \
                           "setpts=PTS-STARTPTS," \
                           "split=2[stream{i1}out1][stream{i1}out2];" \
                .format(i=i, i1=i + 1, width=WIDTH, height=HEIGHT, fps=FPS)

    # 5. APPLY PADDING
    for i in range(number_files):
        i += 1
        FULL_SCRIPT += "[stream{i}out1]pad=width={width}:height={height}:x=({width}-iw)/2:y=({height}-ih)/2:color={bg_color}," \
                       "trim=duration={img_duration}," \
                       "select=lte(n\,{img_frame_count})[stream{i}overlaid];" \
            .format(i=i, width=WIDTH, height=HEIGHT,
                    bg_color=BACKGROUND_COLOR, img_duration=IMAGE_DURATION, img_frame_count=IMAGE_FRAME_COUNT)
        if i == 1:
            FULL_SCRIPT += "[stream{i}out2]pad=width={width}:height={height}:x=({width}-iw)/2:y=({height}-ih)/2:color={bg_color}," \
                           "trim=duration={trans_duration}," \
                           "select=lte(n\,{trans_frame_count})," \
                           "fade=t=out:s=0:n={trans_frame_count}[stream{i}fadeout];" \
                .format(i=i, width=WIDTH, height=HEIGHT,
                        bg_color=BACKGROUND_COLOR,
                        trans_duration=TRANSITION_DURATION,
                        trans_frame_count=TRANSITION_FRAME_COUNT)
        elif i < number_files:
            FULL_SCRIPT += "[stream{i}out2]pad=width={width}:height={height}:x=({width}-iw)/2:y=({height}-ih)/2:color={bg_color}," \
                           "trim=duration={trans_duration}," \
                           "select=lte(n\,{trans_frame_count})," \
                           "split=2[stream{i}starting][stream{i}ending];" \
                .format(i=i, width=WIDTH, height=HEIGHT,
                        bg_color=BACKGROUND_COLOR,
                        trans_duration=TRANSITION_DURATION,
                        trans_frame_count=TRANSITION_FRAME_COUNT)
        elif i == number_files:
            FULL_SCRIPT += "[stream{i}out2]pad=width={width}:height={height}:x=({width}-iw)/2:y=({height}-ih)/2:color={bg_color}," \
                           "trim=duration={trans_duration}," \
                           "select=lte(n\,{trans_frame_count})," \
                           "fade=t=in:s=0:n={trans_frame_count}[stream{i}fadein];" \
                .format(i=i, width=WIDTH, height=HEIGHT,
                        bg_color=BACKGROUND_COLOR,
                        trans_duration=TRANSITION_DURATION,
                        trans_frame_count=TRANSITION_FRAME_COUNT)

        if i != 1 and i != number_files:
            FULL_SCRIPT += "[stream{i}starting]fade=t=in:s=0:n={trans_frame_count}[stream{i}fadein];" \
                .format(i=i, trans_frame_count=TRANSITION_FRAME_COUNT)
            FULL_SCRIPT += "[stream{i}ending]fade=t=out:s=0:n={trans_frame_count}[stream{i}fadeout];" \
                .format(i=i, trans_frame_count=TRANSITION_FRAME_COUNT)

    # 6. CREATE TRANSITION FRAMES
    for i in range(1, number_files):
        FULL_SCRIPT += "[stream{i1}fadein][stream{i}fadeout]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2," \
                       "trim=duration={trans_duration}," \
                       "select=lte(n\,{trans_frame_count})[stream{i1}blended];" \
            .format(i1=i + 1, i=i, trans_duration=TRANSITION_DURATION, trans_frame_count=TRANSITION_FRAME_COUNT)

    # 7. BEGIN CONCAT
    for i in range(1, number_files):
        FULL_SCRIPT += "[stream{i}overlaid][stream{i1}blended]".format(i=i, i1=i + 1)

    # 8. END CONCAT
    FULL_SCRIPT += "[stream{img_count}overlaid]concat=n={img_count21}:v=1:a=0,format=yuv420p[video]\"" \
        .format(img_count=number_files, img_count21=2 * number_files - 1)

    # 9. END
    FULL_SCRIPT += " -map [video] -vsync 2 -async 1 -rc-lookahead 0 -g 0 " \
                   "-profile:v main -level 42 -c:v libx264 -r {fps} {output}video.mp4" \
        .format(fps=FPS, output=save_path)
    handle_process_ffmpeg(FULL_SCRIPT)
    return '{}video.mp4'.format(save_path)


def handle_process_ffmpeg(code):
    print(code)
    try:
        subprocess.call(code, shell=True)
    except Exception as e:
        return False


def merge_video_sub(video, sub, name):
    save_path = base_dir + '/media/prods/'
    code = 'ffmpeg -y -i {video} -vf subtitles={sub} {save}.mp4'.format(video=video, sub=sub, save=save_path + name)
    handle_process_ffmpeg(code)
    return '{}.mp4'.format(save_path + name)


def generate_sub(path_file):
    save_path = base_dir + '/media/prods/sub_video.srt'
    code = 'autosub -o {save} -S vi -F srt -D vi {path}'.format(path=path_file, save=save_path)
    handle_process_ffmpeg(code)
    return save_path


def handle_create_video_loop(video=None, audio=None):
    save_path = base_dir + '/media/prods/'
    code = 'ffmpeg -y -i {audio} -filter_complex "movie={video}:loop=0,setpts=N/FRAME_RATE/TB" -shortest {save}prod.mp4'.format(
        video=video, audio=audio, save=save_path)
    handle_process_ffmpeg(code)
    return '{}prod.mp4'.format(save_path)


def handle_create_bg_music(music, audio, volume):
    if music:
        bg_audio = helpers.handle_upload_file(music, music.name, 'music')
        save_path = base_dir + '/media/audio/'
        code = 'ffmpeg -y -i ' + audio + ' -i ' \
               + bg_audio + \
               ' -filter_complex "[0]volume=10[s];' \
               '[1]volume={}[t];' \
               '[t][s]amix=duration=shortest" {}audio-bg.mp3'.format(
                   volume, save_path)
        handle_process_ffmpeg(code)
        return '{}audio-bg.mp3'.format(save_path)


def handle_merge_into_outro(intro=None, video=None, outro=None, name=None):
    save_path = base_dir + '/media/prods/'
    code = 'melt {intro} {video} {outro} -mix 30 -mixer luma -consumer avformat:{save}.mp4 vcodec=libx264'\
        .format(intro=intro, video=video, outro=outro, save=save_path + name)
    handle_process_ffmpeg(code)
    return '{}.mp4'.format(save_path + name)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai

import pyaudio
import json
import subprocess

import time

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 2

CLIENT_ACCESS_TOKEN = ''
SUBSCRIBTION_KEY = ''

def main():
    resampler = apiai.Resampler(source_samplerate=RATE)

    vad = apiai.VAD()

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIBTION_KEY)

    request = ai.voice_request()

    def callback(in_data, frame_count, time_info, status):
        frames, data = resampler.resample(in_data, frame_count)
        state = vad.processFrame(frames)
        request.send(data)

        if (state == 1):
            return in_data, pyaudio.paContinue
        else:
            return in_data, pyaudio.paComplete

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=False,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    stream.start_stream()

    print ("Say!")

    try:
        while stream.is_active():
            time.sleep(0.1)
    except Exception:
        raise e
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()

    print ("Wait for response...")
    response = request.getresponse()

    test = response.read()

    #print (test)

    result = json.loads(test.decode('utf-8'))
    #print(result)
    parameters = result['result']['parameters']

    #print (parameters)

    if parameters['name'] == 'Light':

        cmd = '''curl -v -S -u : -X GET http://#DOMAIN#/v1/device/property?id=12345&property=relay'''
        args = cmd.split()
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        relaypower_status =json.loads(stdout)['relay']

        #print (stdout)

        if relaypower_status == 0:
            print("Fan is off")
        elif relaypower_status == 1:
            print ("Fan is on")
        print (relaypower_status)

if __name__ == '__main__':
    main()

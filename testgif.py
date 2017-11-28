import base64
from urllib.request import urlopen, urlretrieve
import requests
import urllib.parse
import http.client
from urllib import *
import os
from io import StringIO
import struct
import threading
import time
import uuid
import wave
import sys
import pyaudio
import websocket
import requests
from threading import Timer
import json
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pyglet

text = ""
def record(RECORD_TIME):
    
    def get_wave_header(frame_rate):
        """
        Generate WAV header that precedes actual audio data sent to the speech translation service.

        :param frame_rate: Sampling frequency (8000 for 8kHz or 16000 for 16kHz).
        :return: binary string
        """
        if frame_rate not in [8000, 16000]:
            raise ValueError("Sampling frequency, frame_rate, should be 8000 or 16000.")

        nchannels = 1
        bytes_per_sample = 2
        output = StringIO()
        output.write('RIFF\x00\x00\x00\x00WAVEfmt \x12\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00\x00\x00data\x00\x00\x00\x00')
        data = output.getvalue()
        output.close()
        return data

    def on_open(ws):
        """
        Callback executed once the Websocket connection is opened.
        This function handles streaming of audio to the server.

        :param ws: Websocket client.
        """
        print('Connected. Server generated request ID = ', ws.sock.headers['x-requestid'])
        def run(*args):
            """Background task which streams audio."""
            print("Run")
            # Send WAVE header to provide audio format information
            data = get_wave_header(16000)
            ws.send(data, websocket.ABNF.OPCODE_BINARY)
            # Stream pyAudio Microphone Audio
            # while True:                
            for i in range(0, int(RATE / CHUNK * RECORD_TIME)):
                sys.stdout.write('.')
                data = stream.read(CHUNK)
                ws.send(data, websocket.ABNF.OPCODE_BINARY)

            stream.stop_stream()
            stream.close()
            p.terminate()
            ws.close()
            print('Background thread terminating...')

        threading._start_new_thread(run, ())

    def on_close(ws):
        """
        Callback executed once the Websocket connection is closed.

        :param ws: Websocket client.
        """
        print('Connection closed...')
        stream.stop_stream()
        stream.close()
        p.terminate()

    def on_error(ws, error):
        """
        Callback executed when an issue occurs during the connection.
        :param ws: Websocket client.
        """
        print(error)


    def on_data(ws, message, message_type, fin):
        """
        Callback executed when Websocket messages are received from the server.
        :param ws: Websocket client.
        :param message: Message data as utf-8 string.
        :param message_type: Message type: ABNF.OPCODE_TEXT or ABNF.OPCODE_BINARY.
        :param fin: Websocket FIN bit. If 0, the data continues.
        """
        global text
        if message_type == websocket.ABNF.OPCODE_TEXT:
            converted = json.loads(message)
            if converted['type'] =='final':
                # print('\n', converted['recognition'], '\n')
                translated = converted['recognition']
                text= translated
         
    headers = {'Ocp-Apim-Subscription-Key': 'Enter issue Token API Key'}
    payload = {}
    r = requests.post("https://api.cognitive.microsoft.com/sts/v1.0/issueToken", data="", headers=headers)
    token = r.content
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    translate_from = 'en-US'
    translate_to = 'en-US'
    features = "Partial"

    # Transcription results will be saved into a new folder in the current directory
    output_folder = os.path.join(os.getcwd(), uuid.uuid4().hex)

    # These variables keep track of the number of text-to-speech segments received.
    # Each segment will be saved in its own audio file in the output folder.
    tts_state = {'count': 0}

    # Setup functions for the Websocket connection
    client_trace_id = str(uuid.uuid4())
    request_url = "wss://dev.microsofttranslator.com/speech/translate?from={0}&to={1}&features={2}&format={3}&api-version=1.0".format(translate_from, translate_to, features,'audio/wav')

    print("Ready to connect...")
    print("Request URL      = {0})".format(request_url))
    print("ClientTraceId    = {0}".format(client_trace_id))
    print('Results location = %s\n' % (output_folder))

    ws_client = websocket.WebSocketApp(
        request_url,
        header=[
            'Authorization: Bearer ' + token.decode('utf-8'),
            'X-ClientTraceId: ' + client_trace_id
        ],
        on_open=on_open,
        on_data=on_data,
        on_error=on_error,
        on_close=on_close
    )
    ws_client.run_forever()


df2 = pd.read_csv("outputTableSpellCheck.csv")
df2 = df2[df2['phrase']!=""]
df2 = df2[df2['phrase']!="Nan"]
df2 = df2.reset_index(drop=True)
df2['phrase'] = df2['phrase'].apply(lambda x: str(x).capitalize())
df2 = df2[df2['phrase']!="Nan"]
df2 = df2.drop_duplicates()

# pick an animated gif file you have in the working directory
ag_file = "mygif.gif"
# blank_file = "blank.jpg"
# blank = urlretrieve("https://ak4.picdn.net/shutterstock/videos/339694/thumb/1.jpg", blank_file)
# img_file = urlretrieve("https://vignette.wikia.nocookie.net/fallout/images/5/5a/White_Space.gif/revision/latest?cb=20140830141755", ag_file)
# spriteTemp = pyglet.sprite.Sprite(animationTemp)

# create a window and set it to the image size
win = pyglet.window.Window(width=370, height=200)
# set window background color = r, g, b, alpha
# each value goes from 0.0 to 1.0
white = 1, 1, 1, 1
pyglet.gl.glClearColor(*white)

from pyglet.window import key

from pyglet.window import mouse
mybatch = pyglet.graphics.Batch()

gif_sprites = []
def getAnim():
    time.sleep(1)
    URL=str(df2[df2['phrase'].isin(process.extractOne(text, df2['phrase']))]['url'].values[0])
    image_url = URL
    img_file = urlretrieve(image_url, ag_file)
    animation = pyglet.resource.animation(ag_file)
    sprites = pyglet.sprite.Sprite(animation,batch =mybatch)
    gif_sprites.append(sprites)
@win.event
def on_key_press(symbol, modifiers):
    global text
    if symbol == key.ENTER:
        try:
            gif_sprites[-1].delete()
            del gif_sprites[-1]
        except:
            print("recording!")
            text = ""
            record(5)
            getAnim()
        
@win.event
def on_draw():
    win.clear()
    mybatch.draw()

pyglet.app.run()
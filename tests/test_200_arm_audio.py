#!/usr/bin/python3
"""
Description: Run tests for philips lights
"""
import pytest
import threading
import json
import time
import glob
import random
import os
from audio_synapse import RupertAudioSynapse, RupertAudioPlayer

# Setup Data
with open('cfg/test/settings.json', 'r') as settings_file:
	settings_json = settings_file.read()
settings = json.loads(settings_json)

# Start Audio Element Consumer in Daemon thread
audio_consumer = RupertAudioSynapse('cfg/test/settings.json')
# Start the consumer
thread = threading.Thread(target=audio_consumer.listen, args=(['elemental_audio']))
thread.setDaemon(True)
thread.start()
# Just give it a brief pause
time.sleep(1)

# Pick a random test MP3
mp3 = random.choice(glob.glob(os.path.expanduser('~') + '/Music/tests/'  + '*.mp3'))

# Run audio manipulation tests
## Turn on with full birghtness

play_track_vol_75 = { "event_type": "control", "play_track": mp3, "return_topic": "debug_topic",
	"volume": 75, "play": "play" }
set_vol_50 = { "event_type": "control", "volume": 50 }
pause_play = { "event_type": "control", "play": "pause" }
resume =  { "event_type": "control", "play": "play", "volume": 60 }
stop =  { "event_type": "control", "play": "stop" }
restart =  { "event_type": "control", "play": "play" }
audio_tests = [
	(settings, play_track_vol_75, 5),
	(settings, set_vol_50, 5),
	(settings, pause_play, 5),
	(settings, resume, 5),
	(settings, stop, 5),
	(settings, restart, 5),
	(settings, stop, 1) ]
@pytest.mark.parametrize("settings,event,sleep_time", audio_tests)
def test_light_element(settings, event, sleep_time):
	audio_producer = RupertAudioPlayer('cfg/test/settings.json')
	audio_producer.send_txt(settings['kafka']['topics']['elemental_audio'], json.dumps(event))
	time.sleep(sleep_time)

import json
import time
from flask import Flask
from markupsafe import escape
from rupert.shared.synapse import Synapse

app = Flask(__name__)

@app.route("/audio/play/<room>/<file>/<volume>")
def play(room, file, volume):
  stop =  { "event_type": "control", "play": "stop" }
  play_track = { "event_type": "control", "play_track": f"/home/rupert/Music/Relax/{escape(file)}.mp3", "return_topic": "debug_topic", "volume": escape(volume), "play": "play" }
  kafka_producer = Synapse('/web/cfg/settings.json')
  kafka_producer.send("bedroom_audio_alpha",json.dumps(stop))
  time.sleep(1)
  kafka_producer.send("bedroom_audio_alpha",json.dumps(play_track)) 
  return f"Play Room: {escape(room)} File: {escape(file)}"

@app.route("/audio/stop/<room>")
def stop(room):
  stop = { "event_type": "control", "play": "stop" }
  kafka_producer_stop = Synapse('/web/cfg/settings.json')
  kafka_producer_stop.send("bedroom_audio_alpha",json.dumps(stop))
  return f"Stop Room: {escape(room)}"

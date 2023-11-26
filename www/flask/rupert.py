import json
import time
from flask import Flask
from markupsafe import escape
from rupert.shared.synapse import Synapse

app = Flask(__name__)

@app.route("/audio/play/<room>/<file>/<volume>")
def play(room, file, volume):
  stop =  { "event_type": "control", "play": "stop" }
  play_track = { "event_type": "control", "play_tracks": [f"/home/rupert/Music/Relax/{escape(file)}.mp3"], "return_topic": "debug_topic", "volume": escape(volume), "play": "play" }
  kafka_producer = Synapse('/web/cfg/settings.json')
  kafka_producer.send("bedroom_audio_alpha",json.dumps(stop))
  time.sleep(1)
  kafka_producer.send("bedroom_audio_alpha",json.dumps(play_track)) 
  return f"Play Room: {escape(room)} File: {escape(file)}"


@app.route("/audio/play/<room>/<file>/<volume>")
def play_list(room, file, volume):
  with open(f"lists/{escape(file)}", 'r', encoding='utf-8') as list_file:
    list_file_json = list_file.read()
  list = json.loads(list_file_json)
  stop =  { "event_type": "control", "play": "stop" }
  play_track = { "event_type": "control", "play_tracks": list, "return_topic": "debug_topic", "volume": escape(volume), "play": "play" }
  kafka_producer = Synapse('/web/cfg/settings.json')
  kafka_producer.send("bedroom_audio_alpha",json.dumps(stop))
  time.sleep(1)
  kafka_producer.send("bedroom_audio_alpha",json.dumps(play_track)) 
  return f"Play Room: {escape(room)} List: {escape(file)}"

@app.route("/audio/stop/<room>")
def stop(room):
  stop = { "event_type": "control", "play": "stop" }
  kafka_producer_stop = Synapse('/web/cfg/settings.json')
  kafka_producer_stop.send("bedroom_audio_alpha",json.dumps(stop))
  return f"Stop Room: {escape(room)}"

#!/usr/bin/python3.11

from rupert_arm_audio.audio_synapse import RupertAudioSynapse, RupertAudioPlayer

audio_consumer = RupertAudioSynapse('cfg/settings.json')

audio_consumer.listen('bedroom_audio')

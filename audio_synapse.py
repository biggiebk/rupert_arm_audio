"""
Description: Contains audio modules
"""
import json
import vlc
import time
from beartype import beartype
from rupert.shared.synapse import Synapse

class RupertAudioSynapse(Synapse):
	"""
		Description: Audio Synapse class.
		Responsible for:
			1. Basic constructor for connecting/starting
			2. Initiates Kafka cosumer
			3. Contains method to push to Kafka as producer
	"""
	@beartype
	def __init__(self, settings_file: str) -> None:
		super().__init__(settings_file=settings_file)
		self.rap = RupertAudioPlayer("")

	@beartype
	def process_event(self, consumer_message) -> None:
		"""
			Description: Initiats events for the requested light
			Responsible for:
				1. Converts the messages value to dictionary
				2. Runs the light event as a daemon thread
			Requires:
				consumer_message
		"""
		control_dict = json.loads(consumer_message.value().decode("utf-8"))
		if control_dict['event_type'] == 'control':
			self.rap.set(control_dict)
		elif control_dict['event_type'] == 'status':
			pass

class RupertAudioPlayer():
	"""
		Description: Handles playing audio
		Responsible for:
			1. Initiating the VLC Player
			2. Controlling playback
	"""
	@beartype
	def __init__(self, options: str='') -> None:
		self.player = vlc.Instance(options)
		self.media_list = None
		self.media_list_player = None
		self.media = None
		self.control_dict = None

	@beartype
	def bye(self) -> None:
		"""Cleans up the the current player"""
		try:
			self.stop()
			self.media_list_player.get_media_player().release()
			del self.media
			del self.media_list_player
			self.player.release()
			del self.player
		except AttributeError:
			pass # do nothing we know this may blow up if something has not already started to play

	@beartype
	def set(self, control_dict: dict[str, set[str, int]]) -> None:
		"""
		Control the audio player. Requries:
			control_dict = Dictionary detailing what controls to execute
		"""
		self.control_dict = control_dict

		if 'play_track' in self.control_dict:
			self.__set_media()

		if 'play' in self.control_dict:
			self.__play_stop_pause()
			time.sleep(1) # Seems to be required in the event we are also updating loop and/or volume after we start.

		if 'loop' in self.control_dict:
			self.__set_loop()

		if 'volume' in self.control_dict:
			self.__set_volume()

## Private methods
	@beartype
	def __play_stop_pause(self) -> None:
		"""
			Starts or stops the player
		"""
		if self.control_dict['play'] == 'stop':
			try: 
				self.media_list_player.get_media_player().stop()
			except:
				pass
		elif self.control_dict['play'] == 'play':
			self.media_list_player.play()
		elif self.control_dict['play'] == 'pause':
			self.media_list_player.pause()
		else:
			raise ValueError(f"Unknown play status: {self.control_dict['play']}")

	@beartype
	def __set_loop(self) -> None:
		"""
			Manipulates looping
		"""
		# current
		if self.control_dict['loop'] == 'current':
			self.media_list_player.set_playback_mode(vlc.PlaybackMode.repeat)
		# play list
		elif self.control_dict['loop'] == 'play_list':
			self.media_list_player.set_playback_mode(vlc.PlaybackMode.loop)
		# end loop
		elif self.control_dict['loop'] == 'end':
			self.media_list_player.set_playback_mode(vlc.PlaybackMode.default)
		else:
			raise ValueError(f"Unknown loop type requested: {self.control_dict['loop']}")

	@beartype
	def __set_media(self) -> None:
		"""
			Sets the playing media
		"""
		# creating a new media list
		self.media_list = self.player.media_list_new()
		# creating a media player object
		self.media_list_player = self.player.media_list_player_new()
		# creating a new media
		self.media = self.player.media_new(self.control_dict['play_track'])
		# adding media to media list
		self.media_list.add_media(self.media)
		# setting media list to the mediaplayer
		self.media_list_player.set_media_list(self.media_list)


	@beartype
	def __set_volume(self) -> None:
		"""
			Adjusts the volume
		"""
		self.media_list_player.get_media_player().audio_set_volume(int(self.control_dict['volume']))


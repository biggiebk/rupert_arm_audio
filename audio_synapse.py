"""
Description: Contains audio modules
"""
import json
import vlc
import time
import ctypes
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
		self.eos = None
	
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
		print(f"  - control f{control_dict}")
		if 'play_tracks' in self.control_dict:
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
	def __event_played(self, event):
		print("__event_played!")
		print(f"  {type(event.u)}")

	def __event_stopped(self, event):
		print("__event_stopped!")

	def __event_ItemAdded(self, event):
		print("__ItemAdded!")

	def __event_WillAddItem(self, event):
		print("__WillAddItem!")

	def __event_ItemDeleted(self, event):
		print("__ItemDeleted!")

	def __event_WillDeleteItem(self, event):
		print("__WillDeleteItem!")

	def __event_EndReached(self, event):
		print("__EndReached!")

	def __event_ViewItemAdded(self, event):
		print("__ViewItemAdded!")

	def __event_ViewWillAddItem(self, event):
		print("__ViewWillAddItem!")

	def __event_ViewItemDeleted(self, event):
		print("__ViewItemDeleted!")

	def __event_ViewWillDeleteItem(self, event):
		print("__ViewWillDeleteItem!")

	def __event_NextItemSet(self, event):
		print("__NextItemSet!")
		print(f"  {event.u.new_length}")

	def __event_VlmMediaAdded(self, event):
		print("__event_VlmMediaAdded!")

	def __event_VlmMediaRemoved(self, event):
		print("__event_VlmMediaRemoved!")

	def __event_VlmMediaChanged(self, event):
		print("__event_VlmMediaChanged!")

	def __event_VlmMediaInstanceStarted(self, event):
		print("__event_VlmMediaInstanceStarted!")

	def __event_VlmMediaInstanceStopped(self, event):
		print("__event_VlmMediaInstanceStopped!")

	def __event_VlmMediaInstanceStatusInit(self, event):
		print("__event_VlmMediaInstanceStatusInit!")

	def __event_VlmMediaInstanceStatusOpening(self, event):
		print("__event_VlmMediaInstanceStatusOpening!")

	def __event_VlmMediaInstanceStatusPlaying(self, event):
		print("__event_VlmMediaInstanceStatusPlaying!")

	def __event_VlmMediaInstanceStatusPause(self, event):
		print("__event_VlmMediaInstanceStatusPause!")

	def __event_VlmMediaInstanceStatusEnd(self, event):
		print("__event_VlmMediaInstanceStatusEnd!")

	def __event_VlmMediaInstanceStatusError(self, event):
		print("__event_VlmMediaInstanceStatusError!")

	def __event_MediaMetaChanged(self, event):
		print("__event_MediaMetaChanged!")

	def __event_MediaSubItemAdded(self, event):
		print("__event_MediaSubItemAdded!")

	def __event_MediaDurationChanged(self, event):
		print("__event_MediaDurationChanged!")

	def __event_MediaParsedChanged(self, event):
		print("__event_MediaParsedChanged!")

	def __event_MediaFreed(self, event):
		print("__event_MediaFreed!")

	def __event_MediaStateChanged(self, event):
		print("__event_MediaStateChanged!")

	def __event_MediaSubItemTreeAdded(self, event):
		print("__event_MediaSubItemTreeAdded!")



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
		print(f"Playing {self.control_dict['play_tracks']}")
		self.media_list = self.player.media_list_new()
		# creating a media player object
		self.media_list_player = self.player.media_list_player_new()
		# creating a new media
		# if array
		if isinstance(self.control_dict['play_tracks'], list):
			for media in self.control_dict['play_tracks']:
				print(media)
				self.media = self.player.media_new(media)
				self.media_list.add_media(self.media)
		else:
			print("Not a list")
			self.media = self.player.media_new(self.control_dict['play_track'])
			# adding media to media list
			self.media_list.add_media(self.media)

		# setting media list to the mediaplayer
		self.media_list_player.set_media_list(self.media_list)
		media_events = self.media.event_manager()
	
		# Event callbacks.
		events = self.media_list_player.event_manager()
		media_events = self.media.event_manager()
		events.event_attach(vlc.EventType.MediaListPlayerPlayed, self.__event_played)
		events.event_attach(vlc.EventType.MediaListPlayerStopped, self.__event_stopped)
		events.event_attach(vlc.EventType.MediaListItemAdded, self.__event_ItemAdded)
		events.event_attach(vlc.EventType.MediaListWillAddItem, self.__event_WillAddItem)
		events.event_attach(vlc.EventType.MediaListItemDeleted, self.__event_ItemDeleted)
		events.event_attach(vlc.EventType.MediaListWillDeleteItem, self.__event_WillDeleteItem)
		events.event_attach(vlc.EventType.MediaListEndReached, self.__event_EndReached)
		events.event_attach(vlc.EventType.MediaListViewItemAdded, self.__event_ViewItemAdded)
		events.event_attach(vlc.EventType.MediaListViewWillAddItem, self.__event_ViewWillAddItem)
		events.event_attach(vlc.EventType.MediaListViewItemDeleted, self.__event_ViewItemDeleted)
		events.event_attach(vlc.EventType.MediaListViewWillDeleteItem, self.__event_ViewWillDeleteItem)
		events.event_attach(vlc.EventType.MediaListPlayerNextItemSet, self.__event_NextItemSet)

		media_events.event_attach(vlc.EventType.MediaMetaChanged, self.__event_MediaMetaChanged)
		media_events.event_attach(vlc.EventType.MediaSubItemAdded, self.__event_MediaSubItemAdded)
		media_events.event_attach(vlc.EventType.MediaDurationChanged, self.__event_MediaDurationChanged)
		media_events.event_attach(vlc.EventType.MediaParsedChanged, self.__event_MediaParsedChanged)
		media_events.event_attach(vlc.EventType.MediaFreed, self.__event_MediaFreed)
		media_events.event_attach(vlc.EventType.MediaStateChanged, self.__event_MediaStateChanged)
		media_events.event_attach(vlc.EventType.MediaSubItemTreeAdded, self.__event_MediaSubItemTreeAdded)

	@beartype
	def __set_volume(self) -> None:
		"""
			Adjusts the volume
		"""
		self.media_list_player.get_media_player().audio_set_volume(int(self.control_dict['volume']))


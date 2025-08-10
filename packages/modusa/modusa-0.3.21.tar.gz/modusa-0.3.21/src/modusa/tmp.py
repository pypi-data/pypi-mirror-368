#def autocorr(self) -> Self:
#	"""
#	
#	"""
#	raise NotImplementedError
#	r = np.correlate(self.data, self.data, mode="full")
#	r = r[self.data.shape[0] - 1:]
#	r_signal = self.__class__(data=r, sr=self.sr, t0=self.t0, title=self.title + " [Autocorr]")
#	return r_signal

#	#----------------------------
#	# To different signals
#	#----------------------------
#	def to_audio_signal(self) -> "AudioSignal":
#		"""
#		Moves TimeDomainSignal to AudioSignal
#		"""
#		raise NotImplementedError
#		from modusa.signals.audio_signal import AudioSignal
#		
#		return AudioSignal(data=self.data, sr=self.sr, t0=self.t0, title=self.title)
#	
#	def to_spectrogram(
#		self,
#		n_fft: int = 2048,
#		hop_length: int = 512,
#		win_length: int | None = None,
#		window: str = "hann"
#	) -> "Spectrogram":
#		"""
#		Compute the Short-Time Fourier Transform (STFT) and return a Spectrogram object.
#		
#		Parameters
#		----------
#		n_fft : int
#			FFT size.
#		win_length : int or None
#			Window length. Defaults to `n_fft` if None.
#		hop_length : int
#			Hop length between frames.
#		window : str
#			Type of window function to use (e.g., 'hann', 'hamming').
#		
#		Returns
#		-------
#		Spectrogram
#			Spectrogram object containing S (complex STFT), t (time bins), and f (frequency bins).
#		"""
#		raise NotImplementedError
#		import warnings
#		warnings.filterwarnings("ignore", category=UserWarning, module="librosa.core.intervals")
#		
#		from modusa.signals.feature_time_domain_signal import FeatureTimeDomainSignal
#		import librosa
#		
#		S = librosa.stft(self.data, n_fft=n_fft, win_length=win_length, hop_length=hop_length, window=window)
#		f = librosa.fft_frequencies(sr=self.sr, n_fft=n_fft)
#		t = librosa.frames_to_time(np.arange(S.shape[1]), sr=self.sr, hop_length=hop_length)
#		frame_rate = self.sr / hop_length
#		spec = FeatureTimeDomainSignal(data=S, feature=f, feature_label="Freq (Hz)", frame_rate=frame_rate, t0=self.t0, time_label="Time (sec)", title=self.title)
#		if self.title != self._name: # Means title of the audio was reset so we pass that info to spec
#			spec = spec.set_meta_info(title=self.title)
#		
#		return spec
#	#=====================================
	
	#=====================================
	
	#--------------------------
	# Other signal ops
	#--------------------------
	
#	def interpolate(self, to: TimeDomainSignal, kind: str = "linear", fill_value: str | float = "extrapolate") -> TimeDomainSignal:
#		"""
#		Interpolate the current signal to match the time axis of `to`.
#	
#		Parameters:
#			to (TimeDomainSignal): The signal whose time axis will be used.
#			kind (str): Interpolation method ('linear', 'nearest', etc.)
#			fill_value (str or float): Value used to fill out-of-bounds.
#	
#		Returns:
#			TimeDomainSignal: A new signal with values interpolated at `to.t`.
#		"""
#		assert self.y.ndim == 1, "Only 1D signals supported for interpolation"
#		
#		interpolator = interp1d(
#			self.t,
#			self.y,
#			kind=kind,
#			fill_value=fill_value,
#			bounds_error=False,
#			assume_sorted=True
#		)
#		
#		y_interp = interpolator(to.y)
	
#		return self.__class__(y=y_interp, sr=to.sr, t0=to.t0, title=f"{self.title} → interpolated")
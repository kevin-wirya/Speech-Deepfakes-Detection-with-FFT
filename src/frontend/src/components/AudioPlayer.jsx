function AudioPlayer({ audioUrl }) {
  return (
    <div className="audio-player-section visible">
      <div className="audio-player-header">
        <span className="audio-icon">🎧</span>
        <span className="audio-title">Listen to your audio</span>
      </div>
      <audio controls src={audioUrl} />
    </div>
  );
}

export default AudioPlayer;

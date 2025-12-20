function ButtonGroup({ onPredict, onClear, isAnalyzing, hasFile }) {
  return (
    <div className="button-group">
      <button 
        className="predict-btn" 
        onClick={onPredict}
        disabled={!hasFile || isAnalyzing}
      >
        {isAnalyzing ? (
          <>
            <span className="spinner"></span>Analyzing...
          </>
        ) : (
          '🔍 Analyze Audio'
        )}
      </button>
      <button className="clear-btn" onClick={onClear}>
        🗑️ Clear
      </button>
    </div>
  );
}

export default ButtonGroup;

function StatusMessage({ status }) {
  const getClassName = () => {
    let className = 'status-message';
    if (status.type === 'loading') className += ' status-loading';
    else if (status.type === 'error') className += ' status-error';
    else if (status.type === 'success') className += ' status-success';
    return className;
  };

  return (
    <div className={getClassName()}>
      {status.type === 'loading' && <span className="spinner"></span>}
      {status.message}
    </div>
  );
}

export default StatusMessage;

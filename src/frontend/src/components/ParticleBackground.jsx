function ParticleBackground() {
  const particles = [
    { width: 100, height: 100, left: '10%', delay: '0s' },
    { width: 80, height: 80, left: '30%', delay: '2s' },
    { width: 120, height: 120, left: '50%', delay: '4s' },
    { width: 90, height: 90, left: '70%', delay: '1s' },
    { width: 110, height: 110, left: '85%', delay: '3s' },
  ];

  return (
    <>
      {particles.map((particle, index) => (
        <div
          key={index}
          className="particle"
          style={{
            width: `${particle.width}px`,
            height: `${particle.height}px`,
            left: particle.left,
            animationDelay: particle.delay,
          }}
        ></div>
      ))}
    </>
  );
}

export default ParticleBackground;

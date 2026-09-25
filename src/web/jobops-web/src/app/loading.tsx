export default function Loading() {
  return (
    <div className="loading-screen" role="status" aria-live="polite">
      <div className="loading-wordmark">J/O</div>
      <div className="loading-track" aria-hidden="true">
        <i />
      </div>
      <p>Reading the application runway…</p>
    </div>
  );
}

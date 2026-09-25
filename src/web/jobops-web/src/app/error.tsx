"use client";

export default function ErrorState({
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="error-screen">
      <span className="error-code">RUN / INTERRUPTED</span>
      <h1>The control room lost the feed.</h1>
      <p>
        No application action was taken. Retry the read path to restore the current JobOps state.
      </p>
      <button type="button" onClick={reset}>Retry feed</button>
    </div>
  );
}

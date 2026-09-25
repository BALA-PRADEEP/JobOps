import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "JobOps",
  description: "Automated job application control room"
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <div>
              <div className="brand"><span>J</span>JobOps</div>
              <p>Application control room</p>
            </div>
            <nav>
              <a href="#overview">Overview</a>
              <a href="#jobs">Jobs</a>
              <a href="#applications">Applications</a>
              <a href="#system">System</a>
            </nav>
            <div className="safety">
              <strong>Dry-run mode</strong>
              <span>Automatic submission is off.</span>
            </div>
          </aside>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}

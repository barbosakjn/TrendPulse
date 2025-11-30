import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'TrendPulse - Discover Trending Topics',
  description: 'Discover what\'s trending in your niche with AI-powered insights from Google Trends, YouTube, Reddit, and more.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-white antialiased">
        {children}
      </body>
    </html>
  );
}

import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'NFL Prop Lab | Research Terminal', description: 'NFL prop research and matchup intelligence' };
export default function RootLayout({children}:{children:React.ReactNode}) {return <html lang="en"><body>{children}</body></html>}

import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";
import { OperatorProvider } from "@/components/layout/OperatorContext";

// Inter for UI (excellent at small sizes, real tabular figures), JetBrains Mono for
// identifiers -- run ids, evidence ids and hashes are compared character by character, so
// they need a face where 0/O and 1/l/I are unmistakable.
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AEGIS Control Center",
  description:
    "Governed AI decision support and human approval for regulated pharmaceutical workflows: GxP batch review, pharmacovigilance intake, and supply/cold-chain planning.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <body className="min-h-dvh">
        <OperatorProvider>
          <AppShell>{children}</AppShell>
        </OperatorProvider>
      </body>
    </html>
  );
}

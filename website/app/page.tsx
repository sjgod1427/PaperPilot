import { Nav } from "@/components/nav";
import { Hero } from "@/components/hero";
import { PrivacySection } from "@/components/privacy-section";
import { ConnectionCards } from "@/components/connection-cards";
import { SetupWizard } from "@/components/setup-wizard";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <div className="min-h-full bg-pp-bg">
      <Nav />
      <main>
        <Hero />
        <PrivacySection />
        <ConnectionCards />
        <div className="mx-auto max-w-5xl px-6 pb-16">
          <p className="mb-4 font-pp-mono text-sm text-pp-muted">Try it now:</p>
          <SetupWizard />
        </div>
        <section className="border-t border-pp-border bg-pp-surface py-20 text-center">
          <div className="mx-auto max-w-2xl px-6">
            <h2 className="mb-3 font-pp-mono text-2xl font-semibold text-pp-ink">
              Ready to try it?
            </h2>
            <p className="mb-8 text-pp-muted">
              One executable, no account, and nothing leaves your machine.
            </p>
            <a
              href="#"
              className="inline-flex items-center rounded-md bg-[#d9a544] px-[22px] py-[13px] font-pp-mono text-sm font-semibold text-[#1c1508]"
            >
              Download PaperPilot.exe
            </a>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}

"use client";

import styles from "./hero.module.css";

export function Hero() {
  return (
    <section
      id="hero"
      className={`${styles.hero} relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-[60px]`}
    >
      <div className={`${styles.glowWash} absolute inset-0`} />
      <div className={`${styles.gridBg} absolute inset-0 opacity-[0.55]`} />

      <div className={styles.star} style={{ left: "8%", top: "16%", width: 2, height: 2 }} />
      <div
        className={styles.star}
        style={{ left: "92%", top: "22%", width: 3, height: 3, animationDelay: "1s" }}
      />
      <div
        className={styles.star}
        style={{ left: "15%", top: "82%", width: 2, height: 2, animationDelay: "1.6s" }}
      />
      <div
        className={styles.star}
        style={{ left: "6%", top: "70%", width: 2, height: 2, animationDelay: ".4s" }}
      />
      <div
        className={styles.star}
        style={{ left: "95%", top: "88%", width: 2, height: 2, animationDelay: "2.1s" }}
      />
      <div
        className={styles.star}
        style={{ left: "48%", top: "8%", width: 2, height: 2, animationDelay: ".9s" }}
      />

      <div className={styles.streakH} style={{ top: "11%" }} />
      <div className={styles.streakH} style={{ top: "86%", animationDelay: "2s" }} />
      <div className={styles.streakV} style={{ left: "90%", animationDelay: "1.2s" }} />
      <div className={styles.streakV} style={{ left: "6%", animationDelay: "2.6s" }} />

      <div className="relative z-[2] w-full max-w-[980px] text-pp-ink">
        <p className="mb-4 font-pp-mono text-xs tracking-[0.08em] text-pp-muted uppercase">
          MCP server for Claude
        </p>
        <h1 className="m-0 mb-[18px] max-w-[14ch] font-pp-mono text-[42px] leading-[1.18] font-semibold">
          Your research folder,{" "}
          <em className="not-italic text-pp-accent [text-shadow:0_0_18px_rgba(103,232,249,0.5)]">
            typeset into a paper.
          </em>
        </h1>
        <p className="mb-[30px] max-w-[54ch] text-lg text-pp-muted">
          PaperPilot reads your code, data, and notes, resolves the venue&apos;s real formatting
          rules, drafts and compiles a LaTeX paper, then checks it for hallucinated claims.{" "}
          <strong className="text-pp-ink">Runs entirely on your machine</strong> — nothing is
          ever uploaded.
        </p>
        <div className="mb-[50px] flex gap-3.5">
          <a
            href="https://github.com/sjgod1427/PaperPilot/releases/latest/download/PaperPilot.exe"
            className="inline-flex items-center rounded-md bg-[#d9a544] px-[22px] py-[13px] font-pp-mono text-sm font-semibold text-[#1c1508]"
          >
            Download PaperPilot.exe
          </a>
          <a
            href="#connect"
            className="inline-flex items-center rounded-md border border-pp-border bg-transparent px-[22px] py-[13px] font-pp-mono text-sm font-semibold text-pp-ink"
          >
            See how it connects
          </a>
        </div>

        <div className="relative grid grid-cols-[1fr_auto_1fr] items-stretch gap-5">
          {/* Terminal panel */}
          <div className={`${styles.term} overflow-hidden rounded-[10px]`}>
            <div className="flex items-center gap-1.5 border-b border-pp-border bg-[rgba(27,35,45,0.6)] px-3.5 py-2.5">
              <span className="h-[9px] w-[9px] rounded-full bg-pp-border" />
              <span className="h-[9px] w-[9px] rounded-full bg-pp-border" />
              <span className="h-[9px] w-[9px] rounded-full bg-pp-border" />
              <span className="ml-1.5 font-pp-mono text-xs text-pp-muted">research/</span>
            </div>
            <div className="px-[18px] py-3.5 font-pp-mono text-xs leading-[1.62] text-pp-muted">
              <div className="text-pp-muted-2">code/</div>
              <div>&nbsp;&nbsp;early_exit.py</div>
              <div>&nbsp;&nbsp;baselines.py</div>
              <div>&nbsp;&nbsp;calibration.py</div>
              <div className="mt-1.5 text-pp-muted-2">data/</div>
              <div>&nbsp;&nbsp;main_results.csv</div>
              <div>&nbsp;&nbsp;ablation_threshold.csv</div>
              <div>&nbsp;&nbsp;dataset_stats.csv</div>
              <div className="mt-1.5 text-pp-muted-2">figures/</div>
              <div>&nbsp;&nbsp;accuracy_vs_k.png</div>
              <div>&nbsp;&nbsp;latency_scatter.png</div>
              <div>notes.md</div>
              <div className="mt-2.5">
                &gt; screening <span className="text-pp-ok">done</span>
              </div>
              <div>
                &gt; venue_resolution <span className="text-pp-ok">done</span>
              </div>
              <div>
                &gt; structure_drafting <span className="text-pp-ok">done</span>
              </div>
              <div>
                &gt; humanization
                <span className={styles.cursor} />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-center text-xl text-pp-accent">→</div>

          {/* Paper preview panel */}
          <div
            className={`${styles.paper} flex flex-col rounded-md border border-pp-paper-border bg-pp-paper px-[26px] pt-[26px] pb-5 font-pp-serif text-pp-paper-ink`}
          >
            <div className="mb-3.5 font-pp-mono text-[10px] tracking-[0.07em] text-pp-paper-muted uppercase">
              main.tex · compiled
            </div>
            <div className="mb-1.5 text-center text-[15.5px] leading-[1.3] font-bold">
              Confidence-Gated Early Exit for Efficient Classifier Inference
            </div>
            <div className="mb-1 text-center text-[9.5px] text-pp-paper-muted">
              Anonymous Author(s)
            </div>
            <div className="mb-2.5 text-center text-[9.5px] text-pp-paper-muted">
              Affiliation withheld for double-blind review
            </div>
            <hr className="mt-2.5 mb-3 border-0 border-t border-[#d8cfba]" />
            <div className="mb-3 text-[9px] leading-[1.5] text-justify text-[#4a4238]">
              <b className="font-semibold italic [font-variant:small-caps]">Abstract</b>
              &mdash;Standard deep classifiers run every layer on every input, even when the
              network is already confident after a few layers. We propose confidence-gated early
              exit, which halts inference once per-layer confidence clears a threshold, requiring
              no architectural changes or retraining.
            </div>
            <div className="mb-1.5 text-[9.5px] font-bold tracking-[0.02em]">
              1&nbsp;&nbsp;Introduction
            </div>
            <div className={styles.cols}>
              <p>
                A deep classifier with <i>L</i> layers commits the same compute to every input,
                whether it is easy or hard to classify. Consider an input the network could
                confidently classify after four layers&mdash;it still pays for all twelve, because
                the standard forward pass carries no mechanism for stopping early{" "}
                <span className={styles.cite}>[1]</span>.
              </p>
              <p>
                We study a simple mechanism for addressing this waste. At each layer of an
                already-trained classifier, we compute the softmax confidence of the current
                layer&apos;s prediction. Once this confidence exceeds a fixed threshold τ,
                inference stops immediately and the current prediction is returned{" "}
                <span className={styles.cite}>[2]</span>.
              </p>
              <p>
                Across three benchmark datasets, confidence-gated exit retains 98.6&ndash;99.3% of
                full-network accuracy while running only 61&ndash;76% of layers on average,
                closing most of the gap to an oracle upper bound.
              </p>
            </div>
            <div className="mt-2.5 text-center text-[8px] text-[#a89c85]">1</div>
          </div>
        </div>
      </div>
    </section>
  );
}

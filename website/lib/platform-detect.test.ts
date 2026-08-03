import { describe, expect, it } from "vitest";
import { detectPlatform } from "./platform-detect";

describe("detectPlatform", () => {
  it("detects Windows", () => {
    const ua =
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";
    expect(detectPlatform(ua)).toBe("windows");
  });

  it("detects macOS", () => {
    const ua =
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15";
    expect(detectPlatform(ua)).toBe("mac");
  });

  it("detects Linux", () => {
    const ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";
    expect(detectPlatform(ua)).toBe("linux");
  });

  it("falls back to unknown for anything else", () => {
    expect(detectPlatform("some unrecognized string")).toBe("unknown");
  });
});

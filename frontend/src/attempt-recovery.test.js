import { describe, expect, it } from "vitest";
import { formatRecoveryAge } from "./attempt-recovery";

describe("pending-answer recovery age", () => {
  it("describes a fresh local recovery record", () => {
    expect(formatRecoveryAge(12_000)).toBe("less than a minute ago");
  });

  it("formats minutes and hours without claiming server persistence", () => {
    expect(formatRecoveryAge(125_000)).toBe("2 minute(s) ago");
    expect(formatRecoveryAge(3_600_000)).toBe("1 hour(s) ago");
  });

  it("does not infer age when the device clock moves before the stored save", () => {
    expect(formatRecoveryAge(null)).toBe("age unavailable");
    expect(formatRecoveryAge(-1)).toBe("age unavailable");
  });
});

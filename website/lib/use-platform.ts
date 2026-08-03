"use client";

import { useEffect, useState } from "react";
import { detectPlatform, type Platform } from "./platform-detect";

export function usePlatform(): Platform {
  const [platform, setPlatform] = useState<Platform>("unknown");

  useEffect(() => {
    // navigator doesn't exist during static/server render, so detection
    // must happen post-mount -- the resulting extra render is expected here.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPlatform(detectPlatform(navigator.userAgent));
  }, []);

  return platform;
}

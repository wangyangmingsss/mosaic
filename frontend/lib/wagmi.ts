import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { mantle } from "viem/chains";

export const config = getDefaultConfig({
  appName: "MOSAIC Protocol",
  projectId: "00000000000000000000000000000000",
  chains: [mantle],
  ssr: true,
});

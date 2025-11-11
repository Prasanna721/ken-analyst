import localFont from "next/font/local";

export const instrumentSerif = localFont({
  src: "../public/fonts/instrument-serif.woff2",
  variable: "--font-instrument-serif",
  display: "swap",
});

export const monument = localFont({
  src: [
    {
      path: "../public/fonts/monument-regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../public/fonts/monument-medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../public/fonts/monument-bold.woff2",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-monument",
  display: "swap",
});

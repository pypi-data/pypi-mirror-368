import { createMDX } from "fumadocs-mdx/next"
import { readFileSync } from "fs"

const withMDX = createMDX()
const pkg = JSON.parse(readFileSync("./package.json", "utf-8"))

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
  output: "export",
  pageExtensions: ["js", "jsx", "md", "mdx", "ts", "tsx"],
  basePath: process.env.NODE_ENV === "production" ? "/aegis" : "",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  publicRuntimeConfig: {
    VERSION: pkg.version,
  },
}

export default withMDX(config)

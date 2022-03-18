import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const path = require("path")

// https://vitejs.dev/config/
export default defineConfig({

  plugins: [vue()],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  server: {
    open: true,
    fs: {
      strict: false
    }
    // fs: {
    //   // Allow serving files from one level up to the project root
    //   allow: ['..']
    // }
  },

})

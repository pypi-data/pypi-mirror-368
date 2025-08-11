import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')

  const isLibraryBuild = env.BUILD_TARGET === 'lib';
  const isProd = mode === 'production';

  const baseConfig = {
    plugins: [react()],
    // Set base path for all asset URLs
    server: {
      cors: true,
      // Important: Allow requests from Flask server
      headers: {
        'Access-Control-Allow-Origin': '*'
      }
    },
    resolve: {
      extensions: ['.mjs', '.js', '.mts', '.ts', '.jsx', '.tsx', '.json'], // Ensure proper file extensions
    }
  };

  if (isLibraryBuild) {
    // Library build configuration
    return {
      ...baseConfig,
      build: {
        lib: {
          // Could also be a dictionary or array of multiple entry points
          entry: resolve(__dirname, 'src/client.ts'),
          name: 'RoutelitClient', // The global variable name when used in UMD builds
          // the proper extensions will be added
          fileName: (format) => `routelit-client.${format}${isProd ? '' : '.dev'}.js`
        },
        minify: isProd ? 'esbuild' : false,
        sourcemap: !isProd,
        // Don't clean output directory on second build
        emptyOutDir: isProd,
        rollupOptions: {
          // make sure to externalize deps that shouldn't be bundled
          // into your library
          external: ['react', 'react-dom', 'react/jsx-runtime'], // Added jsx-runtime
          output: {
            // Provide global variables to use in the UMD build
            // for externalized deps
            globals: {
              'react': 'React',
              'react-dom': 'ReactDOM',
              'react/jsx-runtime': 'jsxRuntime',
              './src/client.ts': 'RoutelitClient'
            }
          }
        },
        outDir: 'dist',
      },
      define: isProd ? {
        'process.env.NODE_ENV': '"production"',
      } : {
        'process.env.NODE_ENV': '"development"',
      },
    };
  } else {
    // Default build configuration (for Flask integration)
    return {
      ...baseConfig,
      build: {
        // Relative path from this file to the Flask static directory
        outDir: '../routelit/static',
        base: '/routelit/',
        emptyOutDir: true,
        // Generate manifest for Flask to reference assets
        manifest: true,
        rollupOptions: {
          // Make the vendor a separate entry
          input: {
            app: resolve(__dirname, 'src/main.tsx')
          },
        }
      }
    };
  }
})

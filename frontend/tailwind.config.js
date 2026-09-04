/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#FFF7F2',
          100: '#FFEFE6',
          200: '#FFD9C6',
          300: '#FFB899',
          400: '#FF8D60',
          500: '#F97342', // Signature Coral Peach
          600: '#EA580C', // Deep Peach
          700: '#C2410C',
          800: '#9A3412',
          900: '#7C2D12',
          950: '#431407',
        },
        peach: {
          50: '#FFF9F6',
          100: '#FFF2EB',
          200: '#FFE4D5',
          300: '#FFCCB3',
          400: '#FFAA85',
          500: '#FF8554',
          600: '#F7642B',
          700: '#D44813',
          800: '#A93913',
          900: '#873214',
          950: '#431407'
        },
        // Peach & White surface mapping:
        slate: {
          50: '#FFFFFF',
          100: '#2A140C', // Darkest Espresso
          200: '#3D1F14', // Heading dark
          300: '#522A1A', // Body dark
          400: '#78432F', // Secondary text
          500: '#9E634C', // Subtle text
          600: '#F0C2AE', // Accent border
          700: '#FAD8C8', // Secondary border
          800: '#FDE4D7', // Card border & divider
          850: '#FFF0E8', // Light peach card inner
          900: '#FFF8F4', // Soft peach-white card
          950: '#FFFFFF', // Pure White surface
        },
        dark: {
          800: '#FFF0E8',
          850: '#FFF7F2',
          900: '#FFF8F4',
          950: '#FFFFFF'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

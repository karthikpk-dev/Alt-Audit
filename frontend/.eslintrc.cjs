module.exports = {
  root: true,
  env: { 
    browser: true, 
    es2020: true,
    node: true,
    jest: true
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:react/recommended',
    'plugin:jsx-a11y/recommended',
  ],
  ignorePatterns: [
    'dist', 
    'node_modules',
    'build',
    'coverage',
    '*.config.js',
    '*.config.ts',
    'src/tests/**/*',
    'src/**/*.test.*',
    'src/**/*.spec.*'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
    project: './tsconfig.json',
    tsconfigRootDir: __dirname,
  },
  plugins: [
    'react-refresh',
    'react',
    'jsx-a11y',
    '@typescript-eslint',
  ],
  settings: {
    react: {
      version: 'detect',
    },
  },
  rules: {
    // React Refresh - Vite specific
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],

    // TypeScript - Essential rules only
    '@typescript-eslint/no-unused-vars': [
      'error', 
      { 
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_'
      }
    ],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-non-null-assertion': 'warn',
    '@typescript-eslint/prefer-nullish-coalescing': 'error',
    '@typescript-eslint/prefer-optional-chain': 'error',

    // React - Modern React patterns
    'react/react-in-jsx-scope': 'off', // Not needed with React 17+
    'react/prop-types': 'off', // Using TypeScript for prop validation
    'react/jsx-key': 'error',
    'react/no-unescaped-entities': 'error',
    'react/self-closing-comp': 'error',

    // Accessibility - Most important rules
    'jsx-a11y/alt-text': 'error',
    'jsx-a11y/label-has-associated-control': 'error',
    'jsx-a11y/click-events-have-key-events': 'warn',

    // JavaScript - Essential code quality
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-var': 'error',
    'prefer-const': 'error',
    'prefer-template': 'error',
    'curly': 'error',
    'eqeqeq': ['error', 'always'],
    
    // Security - Critical rules
    'no-eval': 'error',
    'no-implied-eval': 'error',
  },
}

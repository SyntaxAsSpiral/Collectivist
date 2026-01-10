import tseslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import react from 'eslint-plugin-react';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from "globals";

export default [
	{
		files: ["frontend/src/**/*.{ts,tsx}"],
		languageOptions: {
			globals: {
				...globals.browser,
			},
			parser: tsParser,
			parserOptions: {
				project: true,
				tsconfigRootDir: import.meta.dirname,
				ecmaFeatures: {
					jsx: true,
				},
			},
		},
		settings: {
			react: {
				version: 'detect',
			},
		},
		plugins: {
			'@typescript-eslint': tseslint,
			react: react,
			'react-refresh': reactRefresh,
		},
		rules: {
			// TypeScript recommended rules
			...tseslint.configs.recommended.rules,
			
			// React-specific rules
			'react/react-in-jsx-scope': 'off', // Not needed with new JSX transform
			'react/prop-types': 'off', // We use TypeScript for prop validation
			'react-refresh/only-export-components': [
				'warn',
				{ allowConstantExport: true },
			],
			
			// TypeScript rules
			'@typescript-eslint/no-unused-vars': ['error', { 'argsIgnorePattern': '^_' }],
			'@typescript-eslint/no-explicit-any': 'warn',
			
			// General rules
			'no-console': 'warn',
			'prefer-const': 'error',
			'no-var': 'error',
		},
	},
	{
		ignores: [
			"node_modules/**",
			"frontend/dist/**",
			"backend/**",
			"frontend/vite.config.ts",
			"eslint.config.js",
		],
	},
];
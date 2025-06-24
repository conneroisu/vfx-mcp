// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'VFX MCP Server',
			description: 'Professional video editing MCP server with 35+ tools for AI-powered video manipulation',
			logo: {
				src: './src/assets/logo.png',
			},
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/conneroisu/vfx-mcp' },
			],
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Introduction', slug: 'index' },
						{ label: 'Installation', slug: 'getting-started/installation' },
						{ label: 'Quick Start', slug: 'getting-started/quick-start' },
						{ label: 'MCP Integration', slug: 'getting-started/mcp-integration' },
					],
				},
				{
					label: 'Tools Reference',
					items: [
						{ label: 'Overview', slug: 'tools/overview' },
						{ label: 'Basic Operations', slug: 'tools/basic-operations' },
						{ label: 'Audio Processing', slug: 'tools/audio-processing' },
						{ label: 'Effects & Filters', slug: 'tools/effects-filters' },
						{ label: 'Advanced Operations', slug: 'tools/advanced-operations' },
						{ label: 'Analysis & Extraction', slug: 'tools/analysis-extraction' },
						{ label: 'Text & Graphics', slug: 'tools/text-graphics' },
						{ label: 'Specialized Effects', slug: 'tools/specialized-effects' },
					],
				},
				{
					label: 'Guides',
					items: [
						{ label: 'Common Workflows', slug: 'guides/common-workflows' },
						{ label: 'Batch Processing', slug: 'guides/batch-processing' },
						{ label: 'Color Grading', slug: 'guides/color-grading' },
						{ label: 'Audio Editing', slug: 'guides/audio-editing' },
						{ label: 'VFX and Compositing', slug: 'guides/vfx-compositing' },
					],
				},
				{
					label: 'API Reference',
					items: [
						{ label: 'Resource Endpoints', slug: 'api/resources' },
						{ label: 'Tool Signatures', slug: 'api/tool-signatures' },
						{ label: 'Error Handling', slug: 'api/error-handling' },
					],
				},
				{
					label: 'Examples',
					items: [
						{ label: 'Basic Video Editing', slug: 'examples/basic-editing' },
						{ label: 'Audio Processing', slug: 'examples/audio-processing' },
						{ label: 'Visual Effects', slug: 'examples/visual-effects' },
						{ label: 'Automation Scripts', slug: 'examples/automation' },
					],
				},
				{
					label: 'Support',
					items: [
						{ label: 'Troubleshooting', slug: 'support/troubleshooting' },
						{ label: 'FAQ', slug: 'support/faq' },
						{ label: 'Performance Tips', slug: 'support/performance' },
					],
				},
			],
			customCss: [
				'./src/styles/custom.css',
			],
			editLink: {
				baseUrl: 'https://github.com/conneroisu/vfx-mcp/edit/main/docs/',
			},
		}),
	],
});

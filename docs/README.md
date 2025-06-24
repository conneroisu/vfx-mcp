# VFX MCP Server Documentation

[![Built with Starlight](https://astro.badg.es/v2/built-with-starlight/tiny.svg)](https://starlight.astro.build)

This directory contains the comprehensive documentation for the VFX MCP Server, built with Astro and Starlight for a beautiful, fast documentation experience.

## 📚 Documentation Overview

The documentation covers:

- **🚀 Getting Started**: Installation, quick start, and MCP integration
- **🛠️ Tools Reference**: Complete documentation of all 35+ video editing tools
- **📖 Guides**: Common workflows, best practices, and tutorials
- **🔧 API Reference**: Technical documentation and resource endpoints
- **💡 Examples**: Practical usage examples and code samples
- **🆘 Support**: Troubleshooting, FAQ, and performance tips

## 🏗️ Documentation Structure

```
src/content/docs/
├── index.mdx                    # Homepage with overview
├── getting-started/             # Installation and setup
│   ├── installation.md
│   ├── quick-start.md
│   └── mcp-integration.md
├── tools/                       # Tool documentation
│   ├── overview.md
│   ├── basic-operations.md
│   ├── audio-processing.md
│   ├── effects-filters.md
│   ├── advanced-operations.md
│   ├── analysis-extraction.md
│   ├── text-graphics.md
│   └── specialized-effects.md
├── guides/                      # Workflow guides
│   ├── common-workflows.md
│   ├── batch-processing.md
│   ├── color-grading.md
│   ├── audio-editing.md
│   └── vfx-compositing.md
├── api/                         # API reference
│   ├── resources.md
│   ├── tool-signatures.md
│   └── error-handling.md
├── examples/                    # Code examples
│   ├── basic-editing.md
│   ├── audio-processing.md
│   ├── visual-effects.md
│   └── automation.md
└── support/                     # Help and support
    ├── troubleshooting.md
    ├── faq.md
    └── performance.md
```

## 🎨 Features

- **Beautiful Design**: Modern, responsive design with custom CSS styling
- **Interactive Navigation**: Organized sidebar with logical categorization
- **Search Functionality**: Built-in search across all documentation
- **Code Highlighting**: Syntax highlighting for Python, JSON, and bash
- **Mobile Responsive**: Optimized for all device sizes
- **Performance Optimized**: Fast loading and smooth navigation

## 🚀 Development

### Prerequisites

- Node.js 18+ and npm
- Or use the provided Nix environment

### Setup

```bash
# Navigate to docs directory
cd docs

# Install dependencies
npm install

# Start development server
npm run dev
```

### Available Commands

| Command | Action |
|---------|--------|
| `npm run dev` | Start development server at `localhost:4321` |
| `npm run build` | Build production site to `./dist/` |
| `npm run preview` | Preview build locally |
| `npm run astro` | Run Astro CLI commands |

### Using Nix Environment

```bash
# From project root
nix develop

# Navigate to docs and run commands
cd docs
npm run dev
```

## 📝 Content Guidelines

### Writing Style

- **Clear and Concise**: Use simple language and avoid jargon
- **Task-Oriented**: Focus on what users want to accomplish
- **Examples-Heavy**: Include practical code examples
- **Progressive**: Start simple, build to advanced concepts

### Code Examples

- Use realistic file names and paths
- Include expected outputs when helpful
- Provide context for when to use each approach
- Test all code examples for accuracy

### Tool Documentation

Each tool page should include:
- **Purpose**: What the tool does
- **Parameters**: Complete parameter reference
- **Examples**: Multiple usage examples
- **Use Cases**: When to use this tool
- **Performance Notes**: Speed and quality considerations

## 🎯 Content Organization

### Tool Categories

1. **Basic Operations** (4 tools): Essential video manipulation
2. **Audio Processing** (4 tools): Audio extraction, mixing, visualization
3. **Effects & Filters** (5 tools): Enhancement and visual effects
4. **Format Conversion** (2 tools): File format utilities
5. **Advanced Operations** (10 tools): Complex composition and effects
6. **Analysis & Extraction** (4 tools): Content analysis and extraction
7. **Text & Graphics** (2 tools): Text overlays and animation
8. **Specialized Effects** (4 tools): Professional VFX and cinematic effects

### Navigation Structure

- **Getting Started**: New user onboarding
- **Tools Reference**: Complete tool documentation
- **Guides**: Task-oriented tutorials
- **API Reference**: Technical documentation
- **Examples**: Practical code samples
- **Support**: Help and troubleshooting

## 🔧 Customization

### Styling

Custom styles are defined in `src/styles/custom.css`:
- Brand colors and theming
- Component styling (cards, code blocks, tables)
- Responsive design adjustments
- Animation and interaction effects

### Configuration

Main configuration in `astro.config.mjs`:
- Site metadata and SEO
- Navigation structure
- Social links and branding
- Custom CSS integration

## 📊 Performance

The documentation is optimized for:
- **Fast Loading**: Minimal JavaScript, optimized assets
- **SEO Friendly**: Proper meta tags and semantic HTML
- **Accessibility**: WCAG compliant with keyboard navigation
- **Mobile Performance**: Optimized for mobile devices

## 🤝 Contributing

To contribute to the documentation:

1. **Follow the style guide**: Maintain consistency with existing content
2. **Test examples**: Ensure all code examples work correctly
3. **Update navigation**: Add new pages to `astro.config.mjs`
4. **Preview changes**: Use `npm run dev` to preview your changes

### Adding New Pages

1. Create the markdown file in the appropriate directory
2. Add frontmatter with title and description
3. Update the navigation in `astro.config.mjs`
4. Link from related pages as appropriate

## 🔗 Related Links

- **Main Project**: [VFX MCP Server](../)
- **Starlight Docs**: [starlight.astro.build](https://starlight.astro.build/)
- **Astro Docs**: [docs.astro.build](https://docs.astro.build/)
- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)

---

**Questions about the documentation?** Open an issue or check the [FAQ](src/content/docs/support/faq.md) for common questions.
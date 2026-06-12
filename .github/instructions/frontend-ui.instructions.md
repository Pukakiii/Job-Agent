---
applyTo: "**"
---


## UI stack

---

## Applies to: frontend/ (UI components, pages, layouts)

## UI stack

### Libraries and registries

- shadcn/ui (Nova preset, Base UI) — functional primitives
  Install via MCP: ask agent to add component by name
  Manual: npx shadcn@latest add <component>
- Magic UI (@magicui registry) — animated components
  Install via MCP or: npx shadcn@latest add "@magicui/<component>"
- Tailwind CSS v4 — already installed
- Motion (framer-motion) — only for custom animations not in Magic UI

### MCP servers available (use these, don't install manually)

- shadcn MCP: browse, search, install any shadcn component by description
- Magic UI MCP: look up available Magic UI components and their props
- 21st.dev MCP: generate custom components with /ui command

### Component locations

- src/components/ui/ ← shadcn components (auto-installed)
- src/components/ui/magic/ ← Magic UI components
- src/components/ ← composed project components
- src/features/<domain>/ ← domain components (jobs, cvs, applications)

### Which library for what

- Forms, inputs, dialogs, dropdowns, tables, modals → shadcn/ui
- Sidebar, navigation, breadcrumb, tabs → shadcn/ui
- Stat cards with animated numbers → shadcn Card + Magic UI NumberTicker
- Primary CTA buttons on landing → Magic UI ShimmerButton
- Hero section → Magic UI Particles background + GradualSpacing headline
- Page section entry animation → Magic UI BlurFade (landing only)
- Job score display → Magic UI NumberTicker (mono font, accent color)
- Custom components not in either library → 21st.dev /ui command

### Agent workflow — always follow this order

1. Ask shadcn MCP if component exists → install it
2. Check Magic UI MCP for animated variant → install if needed
3. If neither covers the need → use /ui to generate it
4. Never write component primitives from scratch
5. Never manually copy-paste component source from documentation

### Design system — always follow docs/DESIGN_REFERENCES.md

- All colors must use CSS variables defined in DESIGN_REFERENCES.md
- All spacing follows Nova preset — do not override without reason
- All animations follow the rules in DESIGN_REFERENCES.md
- Brown accent (#a0673a) is the ONLY accent color in the system
- All neutrals must be warm — never use cold gray

### Rules

- Import from @/components/ui/<name> — never relative paths
- One component per file in src/components/ui/magic/
- Do not modify installed component internals — compose around them
- Always check if Magic UI component needs framer-motion before using
- Respect prefers-reduced-motion in all animation code
- Never use inline styles — Tailwind classes only
- No hardcoded hex values in components — CSS variables only (See <attachments> above for file contents. You may not need to search or read the file again.)

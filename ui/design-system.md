# Design System
## Creator Community Platform

**Version**: 1.0  
**Date**: August 18, 2025  
**Target**: Gen Z/Gen Alpha creators

---

## 1. Brand Identity

### 1.1 Visual Language
- **Aesthetic**: Modern, vibrant, "creative gala" inspired by dating apps and social media
- **Personality**: Energetic, inclusive, professional yet playful
- **Core Values**: Creativity, collaboration, authenticity, accessibility

### 1.2 Color Philosophy
- **Primary**: Gradient-driven with high contrast accessibility
- **Secondary**: Creator-focused warm tones
- **Semantic**: Clear success/warning/error states
- **Dark/Light**: Full parity with WCAG 2.2 AA compliance

---

## 2. Typography

### 2.1 Font Stack
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-display: 'Poppins', 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### 2.2 Type Scale
- **Display**: 48px/52px (hero sections)
- **H1**: 32px/40px (page titles)
- **H2**: 24px/32px (section headers)
- **H3**: 20px/28px (subsections)
- **Body**: 16px/24px (primary text)
- **Small**: 14px/20px (metadata, captions)
- **Micro**: 12px/16px (labels, timestamps)

---

## 3. Layout & Grid

### 3.1 Breakpoints
- **Mobile**: 360px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px - 1439px
- **Large**: 1440px+

### 3.2 Grid System
- **Mobile**: 4-column grid, 16px gutters
- **Tablet**: 8-column grid, 20px gutters
- **Desktop**: 12-column grid, 24px gutters

### 3.3 Spacing Scale
- **4px**: Micro spacing (icon padding)
- **8px**: Small spacing (form elements)
- **16px**: Base spacing (component padding)
- **24px**: Medium spacing (section gaps)
- **32px**: Large spacing (page sections)
- **48px**: XL spacing (major sections)

---

## 4. Component Patterns

### 4.1 Navigation
- **Primary Nav**: Fixed header with 5 core sections
- **Command Palette**: ⌘K global search and actions
- **Contextual Actions**: Inline CTAs on hover/focus

### 4.2 Content Layouts
- **Feed**: Infinite scroll with skeleton loading
- **Profile**: Tab-based with sticky CTA
- **Search**: Split layout (filters + results)
- **Messages**: 3-pane desktop, 2-pane mobile

### 4.3 Interactive Elements
- **Buttons**: Primary, secondary, ghost, icon variants
- **Forms**: Inline validation, auto-save, progress indicators
- **Cards**: Hover states, quick actions, media previews
- **Modals**: Drawer sheets on mobile, centered on desktop

---

## 5. Motion & Animation

### 5.1 Principles
- **Purposeful**: Enhance usability, provide feedback
- **Respectful**: Honor prefers-reduced-motion
- **Performant**: 60fps, GPU-accelerated transforms

### 5.2 Timing Functions
- **Ease-out**: UI entrances (300ms)
- **Ease-in**: UI exits (200ms)
- **Spring**: Interactive feedback (400ms)

### 5.3 Common Animations
- **Page transitions**: Slide/fade (300ms)
- **Micro-interactions**: Scale/color (150ms)
- **Loading states**: Skeleton shimmer (1.5s loop)

---

## 6. Accessibility Standards

### 6.1 WCAG 2.2 AA Compliance
- **Contrast**: 4.5:1 for normal text, 3:1 for large text
- **Focus**: Visible focus indicators on all interactive elements
- **Keyboard**: Full keyboard navigation support
- **Screen readers**: Semantic HTML, ARIA labels

### 6.2 Inclusive Design
- **Color blind**: Patterns/icons supplement color coding
- **Motor impairments**: 44px minimum touch targets
- **Cognitive**: Clear language, consistent patterns

---

## 7. Performance Targets

### 7.1 Core Web Vitals
- **LCP**: ≤ 2.5s (Largest Contentful Paint)
- **FID**: ≤ 100ms (First Input Delay)
- **CLS**: ≤ 0.1 (Cumulative Layout Shift)

### 7.2 Bundle Targets
- **JavaScript**: ≤ 250KB gzipped
- **CSS**: ≤ 50KB gzipped
- **Images**: WebP/AVIF with fallbacks

---

## 8. Content Strategy

### 8.1 Voice & Tone
- **Voice**: Encouraging, knowledgeable, inclusive
- **Tone**: Adapts to context (celebratory for achievements, supportive for challenges)

### 8.2 Microcopy Guidelines
- **CTAs**: Action-oriented ("Start collaborating", "Share your work")
- **Errors**: Helpful, specific, with clear next steps
- **Empty states**: Encouraging with clear value proposition

---

## 9. Implementation Guidelines

### 9.1 Component Architecture
- **Atomic Design**: Atoms → Molecules → Organisms → Templates
- **Composition**: Prefer composition over inheritance
- **Theming**: CSS custom properties for runtime theme switching

### 9.2 Development Standards
- **Responsive**: Mobile-first approach
- **Progressive Enhancement**: Core functionality without JavaScript
- **Testing**: Visual regression tests for components

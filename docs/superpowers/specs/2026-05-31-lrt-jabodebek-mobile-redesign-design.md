# LRT Jabodebek Mobile-First Redesign — Design Document

**Version:** 1.0
**Date:** 2026-05-31
**Status:** Approved
**Author:** Claude + User Collaboration

---

## 1. Context & Motivation

### Problem Statement
The existing LRT Jabodebek visualization (`public/index.hmtl`) lacks mobile device support. The fixed 300px sidebar, non-responsive header, and absence of touch-optimized interactions make the app unusable on smartphones — the primary use case for commuters checking real-time train positions.

### Opportunity
Re-imagine the UI with a mobile-first approach that preserves all existing functionality:
- Core train position simulation logic
- Schedule data loading (weekdays/weekends/holidays)
- Route geometry interpolation
- Map visualization via Leaflet

### Goals
1. **Responsive:** Fully functional on 320px–428px width (iPhone SE to iPhone 15 Pro Max)
2. **Touch-native:** Use CSS Scroll Snap for sheet navigation, not JS-driven transforms
3. **Theme-flexible:** Dark/light toggle persisted in localStorage
4. **Preserve logic:** Zero changes to position calculation, scheduling, or data loading

---

## 2. Design Direction

### Visual Identity
- **Dark theme** (default): Modern, battery-saving on OLED, familiar to existing users
- **Light theme** (optional): Better outdoor visibility in Jakarta's sunlight
- **Typography:** Space Mono (clock/data), IBM Plex Sans (body text)
- **Accent color:** Teal `#00d4aa` (dark) / `#0d9488` (light)
- **Line colors:** Cibubur cyan `#00c8ff`, Bekasi orange `#ff9900`, Main purple `#a855f7`

### Navigation Pattern
**Bottom Sheet + Floating Toggle (Hybrid Approach)**

```
┌─────────────────────────────────────┐
│  🌙  Floating theme toggle           │
│      (bottom-left corner)            │
│                                     │
│         M A P                       │
│    (Leaflet, always visible)         │
│                                     │
│  ┌─────────────────────────────┐   │
│  │░░░░ DRAG HANDLE (safe zone)░░░│   │ ← Wide touch target
│  ├─────────────────────────────┤   │
│  │ [Kereta] [Stasiun] [Jadwal]  │   │ ← Tab bar
│  ├─────────────────────────────┤   │
│  │                             │   │
│  │    Scrollable content       │   │
│  │    (scroll-snap container)  │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│     ↑ Bottom Sheet (CSS scroll-snap)│
└─────────────────────────────────────┘
```

### Why This Approach?
- **Bottom sheet** provides familiar transit app UX (Grab, Gojek, Google Maps)
- **Floating toggle** keeps sheet drag zone clean — prevents accidental theme toggles
- **Map always visible** — user never loses geographic context
- **CSS Scroll Snap** — native browser momentum, buttery 60fps, no JS animation loops

---

## 3. Layout & Structure

### Mobile Layout (320px–428px)

| Element | Specification |
|---------|---------------|
| **Map container** | 100vw × 100vh, z-index 0 |
| **Bottom sheet** | Fixed to bottom, full width, variable height |
| **Floating toggle** | Fixed position, z-index 1000 |
| **Header (minimal)** | Optional — show only on desktop |

### Bottom Sheet States

| State | Height | Content |
|-------|--------|---------|
| **Collapsed** | 80px | Drag handle + tab bar |
| **Half-expanded** | 45vh | Tabs + scrollable list |
| **Full-expanded** | 85vh | Tabs + full content |

### Sheet Behavior
- **CSS Scroll Snap** drives height transitions
- **Tab content** uses individual snap points
- **No JS transforms** — rely on native scroll momentum
- **Gesture hints** — subtle indicator when scroll position ambiguous

---

## 4. Component Specifications

### 4.1 Drag Handle

```css
.drag-handle {
  width: 40px;
  height: 4px;
  border-radius: 2px;
  background: var(--border);

  /* Centered, safe margin from edges */
  margin: 8px auto 4px;
}

/* Invisible expanded touch target */
.drag-handle-toucharea {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 32px;
  cursor: grab;
  /* No visible content */
}
```

**Purpose:** Wide, low-friction swipe zone. Users swipe anywhere on the top 32px of the sheet to expand/collapse.

---

### 4.2 Tab Bar

```css
.tab-bar {
  display: flex;
  gap: 4px;
  padding: 8px 12px 4px;
  background: var(--bg);
}

.tab-btn {
  flex: 1;
  height: 44px;  /* iOS minimum touch target */
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;

  background: transparent;
  color: var(--text-dim);
  border: none;
  cursor: pointer;

  transition: background 0.2s, color 0.2s;
}

.tab-btn:active {
  background: var(--panel2);
}

.tab-btn.active {
  background: var(--accent);
  color: var(--bg);
}
```

**Accessibility:**
- `role="tablist"`
- `role="tab"` on each button
- `aria-selected` for active state
- `aria-controls` linking to content panels

---

### 4.3 Content Container (CSS Scroll Snap)

```css
.sheet-content {
  height: calc(100vh - 80px);  /* When collapsed: show header only */
  overflow-y: auto;
  overscroll-behavior: contain;

  /* Scroll Snap — MANDATORY ensures always snaps to nearest point */
  scroll-snap-type: y mandatory;
}

.tab-panel {
  scroll-snap-align: start;
  min-height: 100%;
}
```

**Behavior:**
- Each tab's content panel is a scroll-snap point
- Tab change triggers `scrollIntoView()` to snap to correct panel
- Native browser momentum for smooth scrolling

---

### 4.4 Train Card

**Compact State (default):**
```css
.train-card {
  background: var(--panel);
  border-radius: 12px;
  padding: 12px;
  margin: 8px 12px;

  border-left: 4px solid var(--line-color);

  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

/* Line color mapping */
.train-card[data-line="cibubur"] { border-left-color: var(--line-cibubur); }
.train-card[data-line="bekasi"]  { border-left-color: var(--line-bekasi); }
```

**Content:**
```
┌────────────────────────────────────┐
│ [Badge] KA 06    ●→ Harjamukti    │
│              ETA 4 menit            │
└────────────────────────────────────┘
```

**Expanded State (on tap):**
```css
.train-card.expanded {
  padding-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.progress-bar {
  height: 6px;
  border-radius: 3px;
  background: var(--panel2);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--line-color);
  border-radius: 3px;
  transition: width 0.3s ease;
}
```

**Content:**
```
┌────────────────────────────────────┐
│ [Badge] KA 06    ●→ Harjamukti    │
│ ████████████░░░░░░░░░░░░░░░░░░░░  │
│ Station: Ciliwung → Cikoko         │
│ ETA: 4 menit • Sampai 08:42       │
└────────────────────────────────────┘
```

**Interactions:**
- Tap → toggle expand/collapse
- Tap selected train → deselect, center map on train

---

### 4.5 Station Card

```css
.station-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 12px;
  border-bottom: 1px solid var(--border);

  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.station-card:active {
  background: var(--panel2);
}

.station-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 2px solid var(--line-color);
  background: var(--bg);
}

.station-card[data-line="main"] .station-dot { border-color: var(--line-main); }
.station-card[data-line="cibubur"] .station-dot { border-color: var(--line-cibubur); }
.station-card[data-line="bekasi"] .station-dot { border-color: var(--line-bekasi); }

.station-name {
  font-weight: 500;
  flex: 1;
}

.next-train-time {
  font-size: 0.875rem;
  color: var(--accent);
  font-weight: 500;
}
```

**Content:**
```
┌────────────────────────────────────┐
│ ● Station Name         Next: 3m   │
└────────────────────────────────────┘
```

---

### 4.6 Floating Theme Toggle

```css
.theme-toggle {
  position: fixed;
  bottom: 16px;
  left: 16px;
  z-index: 1000;

  width: 48px;
  height: 48px;
  border-radius: 24px;

  background: var(--panel);
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);

  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;

  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  cursor: pointer;

  transition: transform 0.2s, background 0.3s;
}

.theme-toggle:hover {
  transform: scale(1.05);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.theme-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

**Icon states:**
- 🌙 = dark mode (currently light)
- ☀️ = light mode (currently dark)

**Behavior:**
1. Tap toggles `data-theme` attribute on `<html>`
2. CSS variable cascade applies new colors
3. Preference saved to `localStorage`

---

### 4.7 Schedule Panel

```css
.schedule-section {
  padding: 12px;
}

.schedule-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.schedule-row {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.875rem;
}

.schedule-time {
  font-family: 'Space Mono', monospace;
  color: var(--accent);
  min-width: 50px;
}

.schedule-dest {
  flex: 1;
}

.schedule-status {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.status-running {
  background: var(--accent);
  color: var(--bg);
}

.status-waiting {
  background: var(--panel2);
  color: var(--text-dim);
}

.status-done {
  opacity: 0.5;
}
```

---

## 5. Color Palette

### Dark Theme (Default)

```css
:root,
:root[data-theme="dark"] {
  --bg: #0a0e17;
  --panel: #111722;
  --panel2: #161d2c;
  --border: #1e2d45;

  --accent: #00d4aa;
  --accent2: #ff6b35;

  --line-cibubur: #00c8ff;
  --line-bekasi: #ff9900;
  --line-main: #a855f7;

  --text: #e2e8f0;
  --text-dim: #64748b;
  --text-bright: #f8fafc;

  --glow: rgba(0, 212, 170, 0.15);

  --scroll-thumb: #334155;
  --scroll-track: transparent;
}
```

### Light Theme

```css
:root[data-theme="light"] {
  --bg: #f8fafc;
  --panel: #ffffff;
  --panel2: #f1f5f9;
  --border: #e2e8f0;

  --accent: #0d9488;
  --accent2: #ea580c;

  --line-cibubur: #0891b2;
  --line-bekasi: #c2410c;
  --line-main: #7c3aed;

  --text: #1e293b;
  --text-dim: #64748b;
  --text-bright: #0f172a;

  --glow: rgba(13, 148, 136, 0.1);

  --scroll-thumb: #cbd5e1;
  --scroll-track: #f1f5f9;
}
```

---

## 6. Gesture Handling (CSS Scroll Snap Primary)

### Philosophy
**CSS Scroll Snap drives the experience. JavaScript observes and syncs state only.**

### Implementation

```css
/* Sheet container with snap points */
.bottom-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;

  background: var(--bg);
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.3);

  /* Snap configuration — MANDATORY for firm, decisive snapping */
  scroll-snap-type: y mandatory;
  overscroll-behavior: contain;
}

/* Snap points at each state */
.snap-collapsed {
  scroll-snap-align: start;
  scroll-snap-stop: always;
}

.snap-half {
  scroll-snap-align: start;
}

.snap-full {
  scroll-snap-align: start;
  scroll-snap-stop: always;  /* Prevent accidental scroll past */
}
```

### State Snap Points

```html
<div class="bottom-sheet" id="sheet">
  <!-- Drag handle (no snap) -->
  <div class="drag-area"></div>

  <!-- Tab bar (no snap) -->
  <div class="tab-bar">...</div>

  <!-- Content with snap points -->
  <div class="sheet-content">
    <div class="snap-point snap-collapsed" data-state="collapsed">
      <!-- Empty or minimal content when collapsed -->
    </div>

    <div class="snap-point snap-half" data-state="half">
      <!-- Half-expanded content -->
    </div>

    <div class="snap-point snap-full" data-state="full">
      <!-- Full content -->
    </div>
  </div>
</div>
```

### JavaScript: State Observer via IntersectionObserver

**Philosophy:** CSS Scroll Snap drives the experience. JavaScript observes and syncs state using IntersectionObserver — zero layout thrashing, runs off main thread.

```javascript
// IntersectionObserver for snap-point detection
// Runs off main thread — no layout thrashing, no jank
const sheet = document.getElementById('sheet');
const content = sheet.querySelector('.sheet-content');

// Observe all snap points
const snapPoints = content.querySelectorAll('.snap-point');

const observer = new IntersectionObserver(
  (entries) => {
    // Find the most visible snap point
    let activeState = 'collapsed';

    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Calculate intersection ratio for ambiguity detection
        const ratio = entry.intersectionRatio;

        if (ratio > 0.5) {
          activeState = entry.target.dataset.state;
        }
      }
    });

    // Sync UI state (drag handle appearance, etc.)
    updateDragHandleForState(activeState);
    updateSheetHeaderForState(activeState);
  },
  {
    root: content,
    threshold: [0, 0.5, 1],  // Trigger at 0%, 50%, 100% visibility
    rootMargin: '0px'
  }
);

// Observe each snap point
snapPoints.forEach(point => observer.observe(point));

// Optional: Cleanup when observer no longer needed
// observer.disconnect();
```

**Why IntersectionObserver?**

| Aspect | scroll event + getBoundingClientRect | IntersectionObserver |
|--------|-------------------------------------|----------------------|
| Performance | Triggers on every scroll tick → layout thrashing | Runs off main thread, browser-optimized |
| Accuracy | Manual calculation, prone to edge cases | Browser-native, pixel-perfect |
| Battery | Heavy, fires constantly during scroll | Lightweight, only fires on visibility change |
| Code complexity | Requires debounce + manual math | Declarative, minimal code |

### Tab Switching

```javascript
function switchTab(tabName) {
  const panel = document.getElementById(`panel-${tabName}`);

  // CSS scroll-snap handles the animation
  // JS only triggers the snap
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Update tab active states
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
    btn.setAttribute('aria-selected', btn.dataset.tab === tabName);
  });
}
```

### Why This Approach?

| Aspect | CSS Scroll Snap | JS Transform |
|--------|-----------------|--------------|
| Performance | Native, 60fps, GPU-accelerated | JS-driven, prone to jank |
| Momentum | Native browser physics | Requires custom implementation |
| Accessibility | Native scroll, screen reader works | Breaks standard navigation |
| Code complexity | Minimal CSS | Complex animation loops |
| Edge cases | Handled by browser | Must be manually coded |

---

## 7. Mobile Map Optimizations

### Marker Sizes (Larger for Touch)

```css
.train-marker {
  width: 20px;   /* Desktop: 14px */
  height: 20px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

.train-marker.selected::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--train-color);
  opacity: 0.3;
  animation: pulse 1.5s ease-out infinite;
}

@keyframes pulse {
  0%   { transform: translate(-50%, -50%) scale(0.8); opacity: 0.5; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}
```

### Control Positions

```css
/* Reposition for thumb reach */
.leaflet-control-zoom {
  bottom: 100px;  /* Above toggle */
  right: 16px;
}

.leaflet-control-compass {
  top: 16px;
  right: 16px;
}
```

### Map Settings

```javascript
const map = L.map('map', {
  center: [-6.2600, 106.9200],
  zoom: 12,
  zoomControl: true,
  attributionControl: true,

  // Touch-optimized
  tap: true,
  touchZoom: true,
  scrollWheelZoom: false,  // Disable on mobile to prevent scroll hijack
});
```

---

## 8. Responsive Breakpoints

```css
/* Base: Mobile-first (320px - 428px) */

/* Tablet (640px - 1023px) */
@media (min-width: 640px) {
  .bottom-sheet {
    max-width: 500px;
    margin: 0 auto;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 16px 16px 0 0;
  }

  .theme-toggle {
    bottom: 24px;
    left: calc(50% - 250px - 64px);  /* Centered, offset from sheet */
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .bottom-sheet {
    display: none;
  }

  .theme-toggle {
    top: 16px;
    right: 16px;
    bottom: auto;
    left: auto;
  }

  .sidebar-desktop {
    display: block;
    width: 320px;
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
    background: var(--panel);
    border-left: 1px solid var(--border);
  }
}
```

---

## 9. Accessibility

| Element | Implementation |
|---------|----------------|
| Tab bar | `role="tablist"`, `role="tab"`, `aria-selected`, `aria-controls` |
| Train cards | `role="article"`, `aria-label` with full train info |
| Theme toggle | `aria-label="Toggle theme"`, `aria-pressed` for state |
| Drag handle | `role="slider"`, `aria-valuenow` for position |
| Scroll container | `role="region"`, `aria-label="Sheet content"` |
| Color contrast | All text meets WCAG AA (4.5:1 minimum) |
| Focus states | Custom `:focus-visible` styles |
| Touch targets | Minimum 44×44px all interactive elements |

---

## 10. Files to Modify

| File | Action |
|------|--------|
| `public/index-redesign-mobile-first.html` | New file — complete mobile redesign |
| `public/index.hmtl` | Unchanged — preserved original |

**Note:** The redesign creates a new file, keeping the original intact for reference and fallback.

---

## 11. Success Criteria

1. ✅ Page loads without errors on iPhone SE (320px width)
2. ✅ Bottom sheet responds to swipe gestures with native momentum
3. ✅ Tab switching snaps to correct panel
4. ✅ Train cards expand/collapse on tap
5. ✅ Theme toggle persists choice in localStorage
6. ✅ Dark/light themes display correctly
7. ✅ Map remains visible and interactive when sheet is expanded
8. ✅ All 18 stations display in station list
9. ✅ Train position updates continue smoothly at 60fps
10. ✅ Schedule data loads correctly (weekdays/weekends/holidays)

---

## 12. Out of Scope

- Changes to core JavaScript logic (position calculation, scheduling)
- Changes to data files (GeoJSON routes, schedule JSON)
- Desktop-specific enhancements beyond preserving existing layout
- Push notifications or real-time API integration
- Offline support / PWA

---

*Document generated through collaborative brainstorming. Approved for implementation.*
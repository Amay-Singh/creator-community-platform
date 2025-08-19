# Search & Discover Wireframe

## Desktop Layout (1024px+)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo] Home Search Create Messages Me              [Avatar] [⚙] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ FILTERS ────┐ ┌─ SEARCH RESULTS ─────────────────────────────┐ │
│ │              │ │                                             │ │
│ │ Search       │ │ [Search: "concept artists"] [🔍] [Map View] │ │
│ │ ┌──────────┐ │ │                                             │ │
│ │ │ Keywords │ │ │ Showing 127 creators • Sort: [Relevance ▼] │ │
│ │ └──────────┘ │ │                                             │ │
│ │              │ │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐    │ │
│ │ Category     │ │ │ [📷] │ │ [🎨] │ │ [🎵] │ │ [📱] │ │ [🎬] │    │ │
│ │ ☑ Digital Art│ │ │ Alex │ │ Maya │ │ Sam  │ │ Rio  │ │ Zoe  │    │ │
│ │ ☐ Music      │ │ │ ⭐4.8 │ │ ⭐4.9 │ │ ⭐4.7 │ │ ⭐4.6 │ │ ⭐4.8 │    │ │
│ │ ☐ Writing    │ │ │ SF   │ │ NYC  │ │ LA   │ │ MIA  │ │ SEA  │    │ │
│ │              │ │ │[View]│ │[View]│ │[View]│ │[View]│ │[View]│    │ │
│ │ Location     │ │ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘    │ │
│ │ ○ 25 miles   │ │                                             │ │
│ │ ○ 50 miles   │ │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐    │ │
│ │ ● 100 miles  │ │ │ [🎭] │ │ [📝] │ │ [🎪] │ │ [🎨] │ │ [🎵] │    │ │
│ │ ○ Remote     │ │ │ Luna │ │ Kai  │ │ Ash  │ │ Dex  │ │ Nova │    │ │
│ │              │ │ │ ⭐4.7 │ │ ⭐4.8 │ │ ⭐4.9 │ │ ⭐4.6 │ │ ⭐4.8 │    │ │
│ │ Experience   │ │ │ CHI  │ │ ATL  │ │ DEN  │ │ PDX  │ │ AUS  │    │ │
│ │ ○ Beginner   │ │ │[View]│ │[View]│ │[View]│ │[View]│ │[View]│    │ │
│ │ ● Intermediate│ │ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘    │ │
│ │ ○ Expert     │ │                                             │ │
│ │              │ │ [Load More Results...]                      │ │
│ │ [Clear All]  │ │                                             │ │
│ │ [Save Search]│ │                                             │ │
│ └──────────────┘ └─────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Mobile Layout (360px)

```
┌─────────────────┐
│ [←] Search [⚙]  │
├─────────────────┤
│                 │
│ [Search Input]  │
│ [🔍] [Filters]   │
│                 │
│ 127 results     │
│ [Sort ▼] [Map]  │
│                 │
│ ┌─────────────┐ │
│ │ [📷] Alex   │ │
│ │ ⭐4.8 • SF   │ │
│ │ Digital Art │ │
│ │ [View][Chat]│ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ [🎨] Maya   │ │
│ │ ⭐4.9 • NYC  │ │
│ │ Illustration│ │
│ │ [View][Chat]│ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ [🎵] Sam    │ │
│ │ ⭐4.7 • LA   │ │
│ │ Music Prod  │ │
│ │ [View][Chat]│ │
│ └─────────────┘ │
│                 │
│ [Load More...]  │
│                 │
└─────────────────┘
```

## Filter Panel (Mobile Drawer)

```
┌─────────────────┐
│ Filters    [✕]  │
├─────────────────┤
│                 │
│ Category        │
│ ☑ Digital Art   │
│ ☐ Music         │
│ ☐ Writing       │
│ ☐ Photography   │
│                 │
│ Location        │
│ ○ 25 miles      │
│ ○ 50 miles      │
│ ● 100 miles     │
│ ○ Remote only   │
│                 │
│ Experience      │
│ ○ Beginner      │
│ ● Intermediate  │
│ ○ Expert        │
│                 │
│ Availability    │
│ ☑ Open now      │
│ ☐ Part-time     │
│ ☐ Full projects │
│                 │
│ Languages       │
│ ☑ English       │
│ ☐ Spanish       │
│ ☐ Mandarin      │
│                 │
│ [Clear] [Apply] │
│                 │
└─────────────────┘
```

## Map View Toggle

```
┌─ MAP VIEW ──────────────────────────────────────┐
│                                                 │
│           [Interactive Map]                     │
│                                                 │
│    📍 Alex (4.8) 📍 Maya (4.9)                  │
│                                                 │
│         📍 Sam (4.7)                            │
│                                                 │
│    📍 Rio (4.6)        📍 Zoe (4.8)            │
│                                                 │
│ [List View] [Zoom: +] [-] [My Location]        │
│                                                 │
│ Selected: Alex Chen                             │
│ ┌─ PREVIEW CARD ─────────────────────────────┐  │
│ │ [📷] Alex Chen • ⭐4.8 • San Francisco      │  │
│ │ Digital artist specializing in character   │  │
│ │ design and concept art...                  │  │
│ │ [View Profile] [Send Message]              │  │
│ └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Interaction States

### Search States
- Empty search: Trending creators and suggested searches
- No results: "Try different filters" with suggestions
- Loading: Skeleton cards with shimmer effect

### Filter States
- Active filters: Pill badges with remove option
- Filter count: "3 filters applied" indicator
- Saved searches: Quick access dropdown

### Card Interactions
- Hover: Lift effect + quick action overlay
- Quick invite: Inline form without navigation
- Bookmarking: Heart icon with animation

# Profile View Wireframe

## Desktop Layout (1024px+)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo] Home Search Create Messages Me              [Avatar] [⚙] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐ ┌─────────────────────────────────────────┐ │
│ │                 │ │                                         │ │
│ │   PROFILE       │ │              MAIN CONTENT               │ │
│ │   SIDEBAR       │ │                                         │ │
│ │                 │ │ ┌─ TABS ─────────────────────────────┐ │ │
│ │ [Avatar 120px]  │ │ │ About Portfolio Links Metrics      │ │ │
│ │                 │ │ └─────────────────────────────────────┘ │ │
│ │ Alex Chen       │ │                                         │ │
│ │ @alexcreates    │ │ ┌─ ABOUT TAB ─────────────────────────┐ │ │
│ │ ⭐ 4.8 (127)     │ │ │                                     │ │ │
│ │                 │ │ │ Bio: Digital artist specializing    │ │ │
│ │ 📍 San Francisco│ │ │ in character design and concept     │ │ │
│ │ 🗣 EN, ES, ZH    │ │ │ art for games and animation...      │ │ │
│ │                 │ │ │                                     │ │ │
│ │ Skills:         │ │ │ Categories: Digital Art, Gaming     │ │ │
│ │ • Digital Art   │ │ │ Experience: 3+ years                │ │ │
│ │ • Character     │ │ │ Availability: Open to projects     │ │ │
│ │ • Concept Art   │ │ │                                     │ │ │
│ │                 │ │ │ Recent Activity:                    │ │ │
│ │ [Invite] [Chat] │ │ │ • Completed 5 collaborations       │ │ │
│ │                 │ │ │ • Posted 3 new portfolio items     │ │ │
│ │ ┌─ ACTIONS ───┐ │ │ │ • Active in 2 project discussions │ │ │
│ │ │ □ Follow    │ │ │                                     │ │ │
│ │ │ ⚐ Report    │ │ │                                     │ │ │
│ │ │ 🔗 Share     │ │ │                                     │ │ │
│ │ └─────────────┘ │ │ └─────────────────────────────────────┘ │ │
│ └─────────────────┘ └─────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Mobile Layout (360px)

```
┌─────────────────┐
│ [←] Profile [⋮] │
├─────────────────┤
│                 │
│  [Avatar 80px]  │
│                 │
│   Alex Chen     │
│  @alexcreates   │
│   ⭐ 4.8 (127)   │
│                 │
│ [Invite] [Chat] │
│                 │
├─ TABS ──────────┤
│About Portfolio  │
├─────────────────┤
│                 │
│ 📍 San Francisco│
│ 🗣 EN, ES, ZH    │
│                 │
│ Bio: Digital    │
│ artist special- │
│ izing in char-  │
│ acter design... │
│                 │
│ Skills:         │
│ • Digital Art   │
│ • Character     │
│ • Concept Art   │
│                 │
│ Categories:     │
│ Digital Art,    │
│ Gaming          │
│                 │
│ [View Portfolio]│
│ [See Projects]  │
│                 │
└─────────────────┘
```

## Tab Content Layouts

### Portfolio Tab
```
┌─ PORTFOLIO ─────────────────────────────────────┐
│                                                 │
│ [Upload New] [Sort: Recent ▼] [Filter: All ▼]  │
│                                                 │
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐        │
│ │ IMG │ │ VID │ │ AUD │ │ IMG │ │ VID │        │
│ │ [♡] │ │ [♡] │ │ [♡] │ │ [♡] │ │ [♡] │        │
│ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘        │
│                                                 │
│ ┌─────┐ ┌─────┐ ┌─────┐                        │
│ │ IMG │ │ DOC │ │ IMG │                        │
│ │ [♡] │ │ [♡] │ │ [♡] │                        │
│ └─────┘ └─────┘ └─────┘                        │
│                                                 │
│ [Load More...]                                  │
└─────────────────────────────────────────────────┘
```

### Links Tab
```
┌─ LINKS ─────────────────────────────────────────┐
│                                                 │
│ Connected Platforms:                            │
│                                                 │
│ ┌─ Instagram ──────────────────┐ [✓ Verified]  │
│ │ @alexcreates                 │               │
│ │ 12.5K followers              │               │
│ └──────────────────────────────┘               │
│                                                 │
│ ┌─ YouTube ────────────────────┐ [✓ Verified]  │
│ │ Alex Creates                 │               │
│ │ 8.2K subscribers             │               │
│ └──────────────────────────────┘               │
│                                                 │
│ ┌─ Spotify ────────────────────┐ [⏳ Pending]   │
│ │ Alex Chen Music              │               │
│ │ 1.2K monthly listeners       │               │
│ └──────────────────────────────┘               │
│                                                 │
│ [+ Add Platform]                                │
└─────────────────────────────────────────────────┘
```

## Interaction Patterns

### Hover States
- Portfolio items: Overlay with view/like/share actions
- Action buttons: Scale 1.05 + shadow increase
- Tab navigation: Underline animation

### Loading States
- Profile data: Skeleton placeholders
- Portfolio grid: Shimmer effect
- Tab switching: Fade transition (300ms)

### Error States
- Failed to load: Retry button with error message
- Restricted content: "Content not available" with reason
- Network issues: Offline indicator with sync status

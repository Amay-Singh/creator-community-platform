# 1:1 Chat Wireframe

## Desktop Layout (1024px+)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo] Home Search Create Messages Me              [Avatar] [⚙] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ CHAT LIST ───┐ ┌─ CONVERSATION ─────────────────────────────┐ │
│ │               │ │                                           │ │
│ │ [Search Chats]│ │ [📷] Alex Chen                    [📞][📹] │ │
│ │               │ │ ● Online • Last seen 2m ago               │ │
│ │ ┌───────────┐ │ │ ─────────────────────────────────────────  │ │
│ │ │ [📷] Alex │ │ │                                           │ │
│ │ │ Hey! Love │ │ │ ┌─ Alex ─────────────────────────────────┐ │ │
│ │ │ your work │ │ │ │ Hey! I love your latest character      │ │ │
│ │ │ 2m ago    │ │ │ │ design. Would you be interested in     │ │ │
│ │ └───────────┘ │ │ │ collaborating on a game project?       │ │ │
│ │               │ │ │ 2:34 PM                                │ │ │
│ │ ┌───────────┐ │ │ └─────────────────────────────────────────┘ │ │
│ │ │ [🎨] Maya │ │ │                                           │ │
│ │ │ Project   │ │ │                     ┌─ You ─────────────┐ │ │
│ │ │ update    │ │ │                     │ Thanks! I'd love  │ │ │
│ │ │ 1h ago    │ │ │                     │ to hear more      │ │ │
│ │ └───────────┘ │ │                     │ about it. What    │ │ │
│ │               │ │                     │ kind of game?     │ │ │
│ │ ┌───────────┐ │ │                     │ 2:35 PM          │ │ │
│ │ │ [🎵] Sam  │ │ │                     └───────────────────┘ │ │
│ │ │ New track │ │ │                                           │ │
│ │ │ 3h ago    │ │ │ ┌─ Alex ─────────────────────────────────┐ │ │
│ │ └───────────┘ │ │ │ It's an indie RPG about time travel.   │ │ │
│ │               │ │ │ I need character concepts for the      │ │ │
│ │ [New Chat +]  │ │ │ main protagonists. Here's the brief:   │ │ │
│ │               │ │ │ [📎 game_brief.pdf]                    │ │ │
│ │               │ │ │ 2:36 PM                                │ │ │
│ │               │ │ └─────────────────────────────────────────┘ │ │
│ │               │ │                                           │ │
│ │               │ │ ─────────────────────────────────────────  │ │
│ │               │ │                                           │ │
│ │               │ │ ┌─ MESSAGE COMPOSER ───────────────────┐   │ │
│ │               │ │ │ [Type a message...] [📎][😊][🎨][🔊] │   │ │
│ │               │ │ │                              [Send] │   │ │
│ │               │ │ └───────────────────────────────────────┘   │ │
│ └───────────────┘ └─────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Mobile Layout (360px)

```
┌─────────────────┐
│ [←] Alex   [📞] │
│ ● Online        │
├─────────────────┤
│                 │
│ ┌─ Alex ───────┐ │
│ │ Hey! I love   │ │
│ │ your latest   │ │
│ │ character     │ │
│ │ design...     │ │
│ │ 2:34 PM       │ │
│ └───────────────┘ │
│                 │
│      ┌─ You ───┐ │
│      │ Thanks! │ │
│      │ I'd love│ │
│      │ to hear │ │
│      │ more... │ │
│      │ 2:35 PM │ │
│      └─────────┘ │
│                 │
│ ┌─ Alex ───────┐ │
│ │ It's an indie │ │
│ │ RPG about     │ │
│ │ time travel...│ │
│ │ [📎 brief.pdf]│ │
│ │ 2:36 PM       │ │
│ └───────────────┘ │
│                 │
│ ┌─ COMPOSER ───┐ │
│ │ [Message...] │ │
│ │ [📎][😊] [▶] │ │
│ └───────────────┘ │
└─────────────────┘
```

## Chat List View (Mobile)

```
┌─────────────────┐
│ Messages   [✏️] │
├─────────────────┤
│                 │
│ [Search chats]  │
│                 │
│ ┌─────────────┐ │
│ │ [📷] Alex   │ │
│ │ Hey! Love   │ │
│ │ your work   │ │
│ │ 2m • 1 new  │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ [🎨] Maya   │ │
│ │ Project     │ │
│ │ update sent │ │
│ │ 1h          │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ [🎵] Sam    │ │
│ │ Check out   │ │
│ │ this track  │ │
│ │ 3h          │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ [🎬] Team   │ │
│ │ Meeting at  │ │
│ │ 3pm today   │ │
│ │ 5h          │ │
│ └─────────────┘ │
│                 │
└─────────────────┘
```

## Message Types & States

### Message Bubbles
```
┌─ Sent Message ──────────────────────────┐
│                    ┌─ You ─────────────┐ │
│                    │ This looks great! │ │
│                    │ ✓✓ 2:35 PM        │ │
│                    └───────────────────┘ │
└─────────────────────────────────────────┘

┌─ Received Message ──────────────────────┐
│ ┌─ Alex ─────────────────────────────────┐ │
│ │ Thanks! Want to see the full series?   │ │
│ │ 2:36 PM                                │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘

┌─ File Attachment ───────────────────────┐
│ ┌─ Alex ─────────────────────────────────┐ │
│ │ [📎] character_concepts.zip             │ │
│ │ 2.4 MB • [Download] [Preview]          │ │
│ │ 2:37 PM                                │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Typing Indicators
```
┌─ Typing ────────────────────────────────┐
│ ┌─ Alex ─────────────────────────────────┐ │
│ │ ● ● ● typing...                        │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Composer Features

### Rich Text Options
- **Bold**, *Italic*, `Code`, ~~Strike~~
- Emoji picker with recent/categories
- File attachment (drag & drop support)
- Voice message recording
- AI assist for message suggestions

### Quick Actions
- **@mentions**: Autocomplete with user search
- **#hashtags**: Project/topic tagging
- **Reactions**: Quick emoji responses
- **Translation**: Auto-detect and translate toggle

## Accessibility Features

### Keyboard Navigation
- Tab through messages chronologically
- Arrow keys for message navigation
- Enter to send, Shift+Enter for new line
- Escape to close modals/drawers

### Screen Reader Support
- Message timestamps announced
- File attachment descriptions
- Typing indicators announced
- Read receipts status announced

### Visual Accessibility
- High contrast mode support
- Reduced motion for animations
- Focus indicators on all interactive elements
- Alternative text for all images/media

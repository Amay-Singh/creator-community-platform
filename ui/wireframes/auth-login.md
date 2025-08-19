# Auth - Login Wireframe

## Layout Structure

```
┌─────────────────────────────────────────┐
│                 HEADER                  │
│  [Logo] Creator Community    [Help] [?] │
├─────────────────────────────────────────┤
│                                         │
│              MAIN CONTENT               │
│                                         │
│    ┌─────────────────────────────┐      │
│    │                             │      │
│    │         LOGIN FORM          │      │
│    │                             │      │
│    │  Welcome Back!              │      │
│    │  Sign in to your account    │      │
│    │                             │      │
│    │  [Email/Username Input]     │      │
│    │  [Password Input] [👁]       │      │
│    │                             │      │
│    │  □ Remember me              │      │
│    │                             │      │
│    │  [Sign In Button - Primary] │      │
│    │                             │      │
│    │  ─────── or ───────         │      │
│    │                             │      │
│    │  [Continue with Google]     │      │
│    │  [Continue with GitHub]     │      │
│    │                             │      │
│    │  Forgot password? [Reset]   │      │
│    │                             │      │
│    │  New here? [Create Account] │      │
│    │                             │      │
│    └─────────────────────────────┘      │
│                                         │
├─────────────────────────────────────────┤
│                 FOOTER                  │
│  Terms • Privacy • Support             │
└─────────────────────────────────────────┘
```

## Mobile Layout (360px)

```
┌─────────────────┐
│ [☰] Logo   [?]  │
├─────────────────┤
│                 │
│   Welcome Back! │
│                 │
│ [Email Input]   │
│ [Password] [👁]  │
│                 │
│ □ Remember me   │
│                 │
│ [Sign In]       │
│                 │
│ ─── or ───      │
│                 │
│ [Google]        │
│ [GitHub]        │
│                 │
│ [Forgot?]       │
│ [Sign Up]       │
│                 │
├─────────────────┤
│ Terms • Privacy │
└─────────────────┘
```

## Interaction States

### Focus States
- Input fields: Blue border + shadow
- Buttons: Scale 1.02 + shadow increase
- Links: Underline + color change

### Error States
- Invalid email: Red border + error message below
- Wrong password: Red border + "Invalid credentials" message
- Network error: Toast notification at top

### Loading States
- Sign In button: Spinner + "Signing in..."
- OAuth buttons: Spinner + disabled state
- Form: Overlay with loading spinner

## Accessibility Notes
- Tab order: Email → Password → Remember → Sign In → OAuth → Links
- ARIA labels for all form elements
- Error announcements for screen readers
- High contrast mode support

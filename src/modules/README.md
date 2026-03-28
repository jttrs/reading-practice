# Practice Modules

Each subdirectory here is a practice module. Modules are registered in `src/pages/Landing.tsx` via the module registry.

## Current Modules

- **decoding/** — Spelling sound decoding practice. Shows a word, then reveals its breakdown into spelling sound elements.
- **sight-words/** — Sight word flashcard practice. Shows a word for the child to read aloud.

## Adding a New Module

1. Create a new directory under `src/modules/` (e.g., `src/modules/my-module/`)
2. Create your module component (e.g., `MyModule.tsx`)
3. Add a route in `src/App.tsx`
4. Add an entry to the module registry in `src/pages/Landing.tsx`:

```ts
{
  id: 'my-module',
  name: 'My Module',
  description: 'Description of what this module practices',
  icon: '📝',
  route: '/my-module',
}
```

## Shared Infrastructure

Modules can use shared hooks from `src/hooks/`:

- `usePracticeSession` — Weighted word selection, queue management, state machine
- `useProgress` — localStorage-based progress tracking (correct/incorrect tallies)
- `useTTS` — Browser text-to-speech with toggle

And shared components from `src/components/`:

- `CooldownIndicator` — SVG radial countdown timer
- `FeedbackButtons` — Green check / red X for correctness feedback

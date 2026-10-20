# 🎥 Creator Recording & Production Checklist

Follow this checklist to record, edit, and assemble the 35-second YouTube Short with maximum visual fidelity and zero AI slop.

---

## 🛠️ 1. Pre-Recording Setup & Environment

- [ ] **Display Resolution & Framing**:
  - Record in 1080x1920 (Vertical 9:16) native canvas OR record full 4K screen (3840x2160) and crop to center 9:16 with keyframe tracking.
  - 60 FPS recording (smooth panning is essential to showcase the 60fps React canvas).
- [ ] **Terminal Aesthetic**:
  - Font: JetBrains Mono / Cascadia Code (size: 20-24pt for clear mobile legibility).
  - Shell theme: Starship / Oh-My-Zsh with clean prompt.
  - Colors: Catppuccin Mocha, Tokyo Night, or GitHub Dark.
- [ ] **Browser Settings**:
  - Hide bookmarks bar and address bar (use full-screen mode or clean window capture).
  - Browser zoom: 125% so station labels and badges are readable on small phone screens.
  - Mouse cursor: Highlighted circular halo (yellow or cyan) or high-contrast macOS pointer.

---

## 🎬 2. Step-by-Step Recording Actions (B-Roll Takes)

- [ ] **Take 1 (0:00 - 0:03) — The Messy Git Log**:
  - In a large multi-branch repo (e.g. linux kernel or complex demo), run:
    ```bash
    git log --graph --oneline --all --decorate -n 30
    ```
  - Capture the dense, unreadable ASCII spaghetti.
- [ ] **Take 2 (0:03 - 0:07) — The Command Launch**:
  - Clear screen (`clear`).
  - Type `python run.py` smoothly.
  - Press `Enter`, wait 0.5s for the FastAPI banner to appear and browser to auto-launch.
- [ ] **Take 3 (0:07 - 0:14) — Smooth Transit Board Pan**:
  - In the browser at `http://localhost:8000`, click and drag smoothly horizontally from left to right.
  - Showcase Yamanote Line (green), Ginza Line (orange), and Marunouchi Line (red) splitting at 45° angles.
- [ ] **Take 4 (0:14 - 0:20) — The Interchange Zoom**:
  - Anchor mouse cursor directly over a 3-way merge station (concentric rings).
  - Scroll trackpad / mousewheel forward to zoom smoothly into 250% scale.
- [ ] **Take 5 (0:20 - 0:26) — Station Drawer & SHA Copy**:
  - Click on the central station circle.
  - Watch drawer slide smoothly in from the right.
  - Hover over and click `[Copy SHA]`. Ensure green checkmark animation triggers.
- [ ] **Take 6 (0:26 - 0:31) — Radar Minimap & Route Isolation**:
  - Whip cursor down to the radar minimap (bottom right) and click once to jump camera.
  - Click `Ginza Line` in the bottom legend pill to dim background lines and highlight the orange route.
- [ ] **Take 7 (0:31 - 0:35) — Snap Fit & Loop Reset**:
  - Press keyboard key `F` to animate full map snap-fit.
  - Cut straight back to the blank terminal cursor from Take 2.

---

## ✂️ 3. Post-Production & Editing (CapCut / Premiere / DaVinci)

- [ ] **Pacing**:
  - Aggressive cut on beat: every cut occurs on the snare/kick of the lo-fi track.
  - Speed ramp long pans (1.3x - 1.5x) to maintain breathless energy.
- [ ] **Kinetic Typography**:
  - Font: Inter Black / Montserrat ExtraBold.
  - Pop-in animation with motion blur (0.1s scale 115% ➔ 100%).
  - Contrast drop shadows (`#000000` with 80% opacity, blur 4px).
- [ ] **Sound Effects (SFX Mixing)**:
  - High pass the music track during the 0:00 - 0:03 hook.
  - Full volume drop on beat at 0:03 with mechanical keyboard `CLACK`.
  - Layer Tokyo JR departure melody chime at 0:07.
  - Crisp click / pop sounds on station selection and button press.
- [ ] **Seamless Loop Verification**:
  - Ensure the audio chord at 0:34.8 resolves seamlessly into the kick/drone at 0:00.0.

---

## 📦 Deliverables Checklist

- [x] Storyboard & Screenplay: `git-subway-map/content/youtube_short_storyboard.md`
- [x] Launch Metadata & SEO: `git-subway-map/content/video_metadata.json`
- [x] Production Checklist: `git-subway-map/content/recording_checklist.md`

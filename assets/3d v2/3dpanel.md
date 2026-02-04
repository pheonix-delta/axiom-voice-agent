This is the **"Wired Brain" Holographic Card** module.

This code is optimized for a single **1/4 screen slot**. It includes a "Holographic Scanner" that runs for 2 seconds to hide the loading process and give that high-tech "Iron Man" feel.

### 1. The Setup (Local Files)

Ensure you have this exact structure for the code to work offline:

```text
/test-folder
  ├── index.html           <-- Paste the code below here
  ├── js/
  │   ├── model-viewer.min.js
  │   └── gsap.min.js
  └── assets/
      └── models/
          └── unitree.glb  <-- Your Unitree Go2 file

```

### 2. The Code (Copy & Paste)

This HTML file simulates the 1/4 screen size so you can see exactly how it fits.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Holographic Card Test</title>
    
    <script type="module" src="./js/model-viewer.min.js"></script>
    <script src="./js/gsap.min.js"></script>

    <style>
        /* --- CORE VARIABLES --- */
        :root {
            --neon-blue: #00f3ff;
            --glass-bg: rgba(10, 15, 30, 0.7);
            --glass-border: rgba(0, 243, 255, 0.2);
            --scan-line: rgba(0, 243, 255, 0.5);
        }

        body {
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-image: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #000 100%);
            font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
        }

        /* --- THE 1/4 CONTAINER (Simulates your grid slot) --- */
        .quarter-slot-simulation {
            width: 450px;  /* Approx 1/4 width on 1080p */
            height: 400px; /* Approx 1/2 height */
            position: relative;
        }

        /* --- THE GLASS CARD --- */
        .holo-card {
            width: 100%;
            height: 100%;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: 0 0 30px rgba(0, 243, 255, 0.1);
            overflow: hidden;
            position: relative;
            
            /* Hidden Start State */
            opacity: 0;
            transform: scale(0.95);
        }

        /* Header Tech */
        .card-header {
            height: 40px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            font-size: 0.8rem;
            color: var(--neon-blue);
            letter-spacing: 2px;
            font-weight: bold;
            background: linear-gradient(90deg, rgba(0,243,255,0.1) 0%, transparent 100%);
        }

        /* The 3D Stage */
        .model-stage {
            width: 100%;
            height: calc(100% - 40px); /* Subtract header */
            position: relative;
        }

        /* Transparent 3D Viewer */
        model-viewer {
            width: 100%;
            height: 100%;
            background-color: transparent;
            opacity: 0; /* Hidden initially */
        }

        /* --- THE SCANNER ANIMATION (Grace Period) --- */
        .scanner-overlay {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 10;
            background: rgba(0,0,0,0.4);
        }

        /* The Laser Line */
        .scan-line {
            width: 100%;
            height: 2px;
            background: var(--neon-blue);
            box-shadow: 0 0 15px var(--neon-blue);
            position: absolute;
            top: 0;
            animation: scanMove 1.5s ease-in-out infinite;
        }

        /* Tech Grid Background for Scanner */
        .scan-grid {
            position: absolute;
            inset: 0;
            background-image: 
                linear-gradient(rgba(0, 243, 255, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            mask-image: linear-gradient(to bottom, transparent, black, transparent);
        }

        .loading-text {
            color: white;
            font-family: monospace;
            background: rgba(0, 243, 255, 0.1);
            padding: 5px 10px;
            border: 1px solid var(--neon-blue);
            font-size: 0.9rem;
            z-index: 2;
        }

        @keyframes scanMove {
            0% { top: 0%; opacity: 0; }
            50% { opacity: 1; }
            100% { top: 100%; opacity: 0; }
        }

        /* --- CONTROLS --- */
        .trigger-btn {
            position: fixed;
            bottom: 30px;
            padding: 15px 40px;
            background: var(--neon-blue);
            border: none;
            font-weight: bold;
            font-size: 1.2rem;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0 0 20px var(--neon-blue);
        }
    </style>
</head>
<body>

    <div class="quarter-slot-simulation">
        
        <div class="holo-card" id="card">
            <div class="card-header">
                <span id="card-title">UNITREE GO2</span>
                <span>● LIVE</span>
            </div>

            <div class="model-stage">
                
                <div class="scanner-overlay" id="scanner">
                    <div class="scan-grid"></div>
                    <div class="scan-line"></div>
                    <div class="loading-text">PROCESSING ASSET...</div>
                </div>

                <model-viewer 
                    id="robot"
                    src="./assets/models/unitree.glb"
                    camera-controls
                    auto-rotate
                    rotation-per-second="30deg"
                    shadow-intensity="1"
                    shadow-softness="0.6"
                    exposure="1.2"
                    environment-image="neutral"
                    disable-zoom
                    camera-orbit="45deg 55deg 2.5m">
                </model-viewer>

            </div>
        </div>

    </div>

    <button class="trigger-btn" onclick="activateHologram()">ACTIVATE</button>

    <script>
        const card = document.getElementById('card');
        const scanner = document.getElementById('scanner');
        const robot = document.getElementById('robot');
        const btn = document.querySelector('.trigger-btn');

        function activateHologram() {
            // 1. Reset everything (for replayability)
            gsap.set(card, { opacity: 0, scale: 0.95 });
            gsap.set(robot, { opacity: 0 });
            scanner.style.display = 'flex';
            scanner.style.opacity = 1;

            // 2. Card "Pop" In
            gsap.to(card, {
                duration: 0.5,
                opacity: 1,
                scale: 1,
                ease: "back.out(1.2)"
            });

            // 3. The 2-Second "Processing" Wait
            // This runs the scanner even if the model loads instantly
            const minWaitTime = 2000; 
            const startTime = Date.now();

            // Check if model is loaded
            const onModelReady = () => {
                const elapsed = Date.now() - startTime;
                const remaining = Math.max(0, minWaitTime - elapsed);

                setTimeout(() => {
                    // 4. Reveal Sequence
                    const tl = gsap.timeline();
                    
                    // Fade out scanner
                    tl.to(scanner, { duration: 0.3, opacity: 0, onComplete: () => scanner.style.display = 'none' });
                    
                    // Fade in robot & add a small "float" animation
                    tl.to(robot, { duration: 0.8, opacity: 1, ease: "power2.out" }, "-=0.1");
                    
                    // Update Button Text
                    btn.textContent = "RESET";
                    btn.onclick = resetDemo;
                }, remaining);
            };

            // If model is already cached/loaded, trigger immediately
            if (robot.loaded) {
                onModelReady();
            } else {
                robot.addEventListener('load', onModelReady, { once: true });
            }
        }

        function resetDemo() {
            gsap.to(card, { duration: 0.3, opacity: 0, scale: 0.9 });
            btn.textContent = "ACTIVATE";
            btn.onclick = activateHologram;
        }
    </script>
</body>
</html>

```

### Why this is the "Best Input":

1. **Scanner Logic:** I added a CSS laser scan (`.scan-line`) that moves up and down over a grid. This is visually much more impressive than a simple spinner.
2. **Container Isolation:** The `.quarter-slot-simulation` div forces the size to 450x400px. This guarantees that when you move it to your main grid, it fits perfectly in the 1/4 slot.
3. **Clean Transparency:** The `backdrop-filter: blur(20px)` ensures that whatever is behind this card (your background, other UI elements) will blur beautifully, maintaining that premium "Glass" aesthetic.

You are asking about **automation**. Currently, your model is static until you drag it. To achieve that premium "Zero-Touch" experience where the model shows off every angle automatically, you need to upgrade the `<model-viewer>` configuration.

Here are the **two levels** of automation you can use.

### Level 1: The "Turntable" (Simple Spin)

This is the standard e-commerce look. The model spins horizontally forever. This works 100% offline.

**Update your HTML tag attributes:**

```html
<model-viewer 
    src="..." 
    auto-rotate              rotation-per-second="30deg" auto-rotate-delay="0"    camera-controls          disable-zoom             >
</model-viewer>

```

* **Limitation:** It only spins **Left ↔ Right**. It will never show the top or bottom of the robot unless the user touches it.

---

### Level 2: The "Wired Brain" Scanner (Cinematic Mode)

To "show the full case" (Top, Bottom, Front, Back) without touching the mouse, you need a **Camera Director Script**. This script will tell the camera to orbit up and down while the model spins.

Add this script to the bottom of your `index.html`. It creates a "Scanning" effect where the camera floats up and down to inspect the robot.

**The Code:**

```javascript
<script>
    const viewer = document.querySelector('model-viewer');

    // CONFIGURATION: The "Scanner" path
    // We oscillate the vertical angle (Phi) between 40deg (High) and 110deg (Low)
    let time = 0;
    const scanSpeed = 0.02; // How fast it looks up/down
    
    function animateScanner() {
        if (!viewer) return;
        
        // 1. Calculate the new vertical angle (Phi)
        // Uses Sine wave for smooth breathing motion
        // 75deg is center. +/- 35deg range.
        const phi = 75 + Math.sin(time) * 35; 
        
        // 2. Get current horizontal angle (Theta) so we don't fight the auto-rotate
        // We let auto-rotate handle the spinning, we just hijack the vertical
        const orbit = viewer.getCameraOrbit();
        const theta = orbit.theta; // Keep existing rotation
        const radius = orbit.radius; // Keep existing zoom
        
        // 3. Apply new Orbit
        // Format: "Theta(rad) Phi(deg) Radius(m)"
        viewer.cameraOrbit = `${theta}rad ${phi}deg ${radius}m`;
        
        time += scanSpeed;
        requestAnimationFrame(animateScanner);
    }

    // Start the scanner when model loads
    viewer.addEventListener('load', () => {
        animateScanner();
    });
</script>

```

### What this does:

1. **Auto-Rotate** handles the **360° Spin**.
2. **The Script** handles the **Vertical Tilt**.
3. **Result:** The camera moves in a smooth "Figure 8" or Wave pattern, inspecting the top of the robot, then sweeping down to inspect the legs/wheels, then back up. It looks like a drone flying around the object.

### Optional: The "Zoom Pulse"

If you want it to look even more high-tech (like it's focusing), change the `const radius` line to this:

```javascript
// Zooms in and out slightly (Breathing effect)
const radius = 2.5 + Math.sin(time * 2) * 0.5; 

```

This will make the camera physically move closer and further away while spinning, ensuring the user sees the "full case" details up close.
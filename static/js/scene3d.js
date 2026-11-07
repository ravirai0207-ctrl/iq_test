/**
 * Advanced 3D Animated Light-Colored Background Engine using Three.js
 * Features a dynamic undulating iridescent silk wave, floating crystalline prisms,
 * luminous pastel particle constellation, and interactive mouse physics.
 */

class Cognitive3DScene {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;

    // 3D Objects
    this.waveMesh = null;
    this.waveGeom = null;
    this.waveOriginalPositions = null;

    this.gemGroup = null;
    this.primaryGem = null;
    this.secondaryGem = null;
    this.ringTorus = null;

    this.particles = null;
    this.particleData = [];

    // Lighting
    this.pointLight1 = null;
    this.pointLight2 = null;
    this.ambientLight = null;

    // Interactive State
    this.mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
    this.clock = new THREE.Clock();
    this.mode = 'idle'; // idle, test, calculating, results

    this.categoryTints = {
      pattern: { c1: 0x6366f1, c2: 0x38bdf8 },
      numerical: { c1: 0x0284c7, c2: 0x06b6d4 },
      spatial: { c1: 0x8b5cf6, c2: 0xd946ef },
      logic: { c1: 0xd97706, c2: 0xf59e0b },
      speed: { c1: 0xe11d48, c2: 0xf43f5e }
    };

    this.init();
  }

  init() {
    if (!this.container) return;

    // 1. Scene setup with soft luminous atmospheric fog
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0xf8fafc, 0.035);

    // 2. Camera setup
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    this.camera.position.set(0, -1, 10);

    // 3. Renderer setup
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0x000000, 0); // Transparent so CSS light gradient shines through
    this.container.appendChild(this.renderer.domElement);

    // 4. Soft Pastel Luminous Lighting
    this.ambientLight = new THREE.AmbientLight(0xffffff, 0.95);
    this.scene.add(this.ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 10, 7);
    this.scene.add(dirLight);

    const backLight = new THREE.DirectionalLight(0xe0e7ff, 0.6);
    backLight.position.set(-6, -8, -5);
    this.scene.add(backLight);

    this.pointLight1 = new THREE.PointLight(0x6366f1, 1.4, 20);
    this.pointLight1.position.set(4, 3, 4);
    this.scene.add(this.pointLight1);

    this.pointLight2 = new THREE.PointLight(0x38bdf8, 1.2, 20);
    this.pointLight2.position.set(-4, -3, 3);
    this.scene.add(this.pointLight2);

    // 5. Construct 3D Elements
    this.buildWaveSurface();
    this.buildFloatingGems();
    this.buildPastelParticles();

    // 6. Listeners
    window.addEventListener('resize', () => this.onWindowResize());
    window.addEventListener('mousemove', (e) => this.onMouseMove(e));

    // 7. Start animation loop
    this.animate();
  }

  buildWaveSurface() {
    // Flowing parametric terrain in background
    const width = 36;
    const height = 36;
    const segmentsX = 54;
    const segmentsY = 54;

    this.waveGeom = new THREE.PlaneGeometry(width, height, segmentsX, segmentsY);
    this.waveOriginalPositions = [];

    const pos = this.waveGeom.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      this.waveOriginalPositions.push({
        x: pos.getX(i),
        y: pos.getY(i),
        z: pos.getZ(i)
      });
    }

    const waveMat = new THREE.MeshPhysicalMaterial({
      color: 0xf8fafc,
      emissive: 0xeef2ff,
      emissiveIntensity: 0.15,
      roughness: 0.25,
      metalness: 0.1,
      transmission: 0.25,
      transparent: true,
      opacity: 0.85,
      side: THREE.DoubleSide,
      flatShading: false
    });

    this.waveMesh = new THREE.Mesh(this.waveGeom, waveMat);
    this.waveMesh.position.set(0, -1.5, -4);
    this.waveMesh.rotation.x = -Math.PI / 3.2;
    this.scene.add(this.waveMesh);
  }

  buildFloatingGems() {
    this.gemGroup = new THREE.Group();
    this.scene.add(this.gemGroup);

    // Primary central crystal (faceted icosahedron)
    const gem1Geom = new THREE.IcosahedronGeometry(1.2, 0);
    const gem1Mat = new THREE.MeshPhysicalMaterial({
      color: 0x4f46e5,
      emissive: 0x312e81,
      emissiveIntensity: 0.15,
      roughness: 0.12,
      metalness: 0.15,
      transmission: 0.7,
      thickness: 1.2,
      transparent: true,
      opacity: 0.85,
      flatShading: true
    });
    this.primaryGem = new THREE.Mesh(gem1Geom, gem1Mat);
    this.primaryGem.position.set(0, 0, 0);
    this.gemGroup.add(this.primaryGem);

    // Gem wireframe shell
    const wireGeom = new THREE.IcosahedronGeometry(1.22, 0);
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x818cf8,
      wireframe: true,
      transparent: true,
      opacity: 0.35
    });
    const wireMesh = new THREE.Mesh(wireGeom, wireMat);
    this.primaryGem.add(wireMesh);

    // Orbiting secondary diamond (octahedron)
    const gem2Geom = new THREE.OctahedronGeometry(0.55, 0);
    const gem2Mat = new THREE.MeshPhysicalMaterial({
      color: 0x06b6d4,
      emissive: 0x083344,
      emissiveIntensity: 0.2,
      roughness: 0.1,
      metalness: 0.2,
      transmission: 0.75,
      transparent: true,
      opacity: 0.8,
      flatShading: true
    });
    this.secondaryGem = new THREE.Mesh(gem2Geom, gem2Mat);
    this.secondaryGem.position.set(2.4, 1.2, 0.5);
    this.gemGroup.add(this.secondaryGem);

    // Orbital ring torus
    const torusGeom = new THREE.TorusGeometry(2.2, 0.02, 16, 100);
    const torusMat = new THREE.MeshBasicMaterial({
      color: 0xa5b4fc,
      transparent: true,
      opacity: 0.45
    });
    this.ringTorus = new THREE.Mesh(torusGeom, torusMat);
    this.ringTorus.rotation.x = Math.PI / 3;
    this.gemGroup.add(this.ringTorus);
  }

  buildPastelParticles() {
    const count = 180;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    const pastelTints = [
      new THREE.Color(0x6366f1), // Indigo
      new THREE.Color(0x38bdf8), // Sky Cyan
      new THREE.Color(0xa855f7), // Purple
      new THREE.Color(0xf472b6), // Rose
      new THREE.Color(0x34d399)  // Emerald
    ];

    for (let i = 0; i < count; i++) {
      const idx = i * 3;
      const x = (Math.random() - 0.5) * 18;
      const y = (Math.random() - 0.5) * 14;
      const z = (Math.random() - 0.5) * 10;

      positions[idx] = x;
      positions[idx + 1] = y;
      positions[idx + 2] = z;

      this.particleData.push({
        x, y, z,
        baseX: x, baseY: y, baseZ: z,
        speed: 0.3 + Math.random() * 0.7,
        phase: Math.random() * Math.PI * 2
      });

      const c = pastelTints[i % pastelTints.length];
      colors[idx] = c.r;
      colors[idx + 1] = c.g;
      colors[idx + 2] = c.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.08,
      vertexColors: true,
      transparent: true,
      opacity: 0.65,
      blending: THREE.NormalBlending
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  }

  onMouseMove(e) {
    const normX = (e.clientX / window.innerWidth) * 2 - 1;
    const normY = -(e.clientY / window.innerHeight) * 2 + 1;
    this.mouse.targetX = normX * 0.45;
    this.mouse.targetY = normY * 0.45;
  }

  onWindowResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  setCategory(categoryKey) {
    const tint = this.categoryTints[categoryKey] || this.categoryTints.pattern;
    const c1 = new THREE.Color(tint.c1);
    const c2 = new THREE.Color(tint.c2);

    if (this.primaryGem && this.primaryGem.material) {
      this.primaryGem.material.color.lerp(c1, 0.75);
    }
    if (this.pointLight1) {
      this.pointLight1.color.lerp(c1, 0.8);
    }
    if (this.pointLight2) {
      this.pointLight2.color.lerp(c2, 0.8);
    }
  }

  celebrate() {
    if (this.primaryGem && this.primaryGem.material) {
      this.primaryGem.material.color.setHex(0x10b981); // Emerald celebration
    }
    if (this.pointLight1) {
      this.pointLight1.color.setHex(0x34d399);
      this.pointLight1.intensity = 2.2;
    }
  }

  pulse() {
    if (this.gemGroup) {
      this.gemGroup.scale.set(1.18, 1.18, 1.18);
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();
    const time = this.clock.getElapsedTime();

    // Mouse parallax lerp
    this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.05;
    this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.05;

    this.camera.position.x = this.mouse.x * 2.0;
    this.camera.position.y = -1 + this.mouse.y * 1.5;
    this.camera.lookAt(0, 0, 0);

    // Animate Flowing 3D Wave Surface
    if (this.waveGeom && this.waveOriginalPositions) {
      const pos = this.waveGeom.attributes.position;
      const count = pos.count;

      for (let i = 0; i < count; i++) {
        const orig = this.waveOriginalPositions[i];
        const u = orig.x * 0.18 + time * 0.6;
        const v = orig.y * 0.18 + time * 0.5;

        const waveZ = Math.sin(u) * Math.cos(v) * 0.9 + Math.sin(u * 1.5 + v * 0.8) * 0.4;
        pos.setZ(i, orig.z + waveZ);
      }
      pos.needsUpdate = true;
    }

    // Animate Floating Crystal Gems
    if (this.gemGroup) {
      // Gentle return to normal scale
      this.gemGroup.scale.lerp(new THREE.Vector3(1, 1, 1), 0.06);

      // Primary crystal rotation & floating
      this.primaryGem.rotation.x += 0.005;
      this.primaryGem.rotation.y += 0.008;

      // Orbit secondary gem
      const orbitRadius = 2.4;
      const orbitSpeed = time * 0.8;
      this.secondaryGem.position.x = Math.cos(orbitSpeed) * orbitRadius;
      this.secondaryGem.position.z = Math.sin(orbitSpeed) * orbitRadius * 0.6;
      this.secondaryGem.position.y = Math.sin(orbitSpeed * 1.4) * 0.7;
      this.secondaryGem.rotation.x += 0.015;
      this.secondaryGem.rotation.y += 0.02;

      // Ring rotation
      this.ringTorus.rotation.z += 0.004;
      this.ringTorus.rotation.x = Math.PI / 3 + Math.sin(time * 0.5) * 0.1;

      // Group floating bob
      this.gemGroup.position.y = Math.sin(time * 1.2) * 0.15;
    }

    // Animate Moving Lights
    if (this.pointLight1 && this.pointLight2) {
      this.pointLight1.position.x = Math.sin(time * 0.7) * 5;
      this.pointLight1.position.y = Math.cos(time * 0.5) * 4;

      this.pointLight2.position.x = Math.cos(time * 0.6) * -5;
      this.pointLight2.position.y = Math.sin(time * 0.8) * -3;
    }

    // Animate Floating Pastel Particles
    if (this.particles && this.particles.geometry) {
      const pos = this.particles.geometry.attributes.position;
      const count = this.particleData.length;

      for (let i = 0; i < count; i++) {
        const p = this.particleData[i];
        const newY = p.baseY + Math.sin(time * p.speed + p.phase) * 0.4;
        const newX = p.baseX + Math.cos(time * p.speed * 0.7 + p.phase) * 0.3;
        pos.setXY(i, newX, newY);
      }
      pos.needsUpdate = true;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

window.Cognitive3DScene = Cognitive3DScene;
